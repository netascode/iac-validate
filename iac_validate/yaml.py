# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

import importlib.util
import logging
import os
import subprocess
from typing import Any, Dict, List

from ruamel import yaml

logger = logging.getLogger(__name__)


class VaultTag(yaml.YAMLObject):
    yaml_tag = "!vault"

    def __init__(self, v: str):
        self.value = v

    def __repr__(self) -> str:
        spec = importlib.util.find_spec("iac_validate.ansible_vault")
        if spec:
            if "ANSIBLE_VAULT_ID" in os.environ:
                vault_id = os.environ["ANSIBLE_VAULT_ID"] + "@" + str(spec.origin)
            else:
                vault_id = str(spec.origin)
            t = subprocess.check_output(
                [
                    "ansible-vault",
                    "decrypt",
                    "--vault-id",
                    vault_id,
                ],
                input=self.value.encode(),
            )
            return t.decode()
        return ""

    @classmethod
    def from_yaml(cls, loader: Any, node: Any) -> str:
        return str(cls(node.value))


class EnvTag(yaml.YAMLObject):
    yaml_tag = "!env"

    def __init__(self, v: str):
        self.value = v

    def __repr__(self) -> str:
        env = os.getenv(self.value)
        if env is None:
            return ""
        return env

    @classmethod
    def from_yaml(cls, loader: Any, node: Any) -> str:
        return str(cls(node.value))


def load_yaml_files(paths: List[str]) -> Dict[str, Any]:
    """Load all yaml files from a provided directory."""

    def _load_file(file_path: str, data: Dict[str, Any]) -> None:
        with open(file_path, "r") as file:
            if ".yaml" in file_path or ".yml" in file_path:
                data_yaml = file.read()
                y = yaml.YAML()
                y.preserve_quotes = True  # type: ignore
                y.register_class(VaultTag)
                y.register_class(EnvTag)
                dict = y.load(data_yaml)
                merge_dict(dict, data)

    result: Dict[str, Any] = {}
    for path in paths:
        if os.path.isfile(path):
            _load_file(path, result)
        else:
            for dir, subdir, files in os.walk(path):
                for filename in files:
                    try:
                        _load_file(dir + os.path.sep + filename, result)
                    except:  # noqa: E722
                        logger.warning("Could not load file: {}".format(filename))
    return result


def merge_list_item(
    source_item: Any, destination: List[Any], merge_list_items: bool = True
) -> None:
    """Merge item into list."""
    if isinstance(source_item, dict) and merge_list_items:
        # check if we have an item in destination with matching primitives
        for dest_item in destination:
            match = True
            comparison = False
            unique_source = False
            unique_dest = False
            for k, v in source_item.items():
                if isinstance(v, dict) or isinstance(v, list):
                    continue
                if k in dest_item and v == dest_item[k]:
                    comparison = True
                    continue
                if k not in dest_item:
                    unique_source = True
                    continue
                comparison = True
                match = False
            for k, v in dest_item.items():
                if isinstance(v, dict) or isinstance(v, list):
                    continue
                if k in source_item and v == source_item[k]:
                    comparison = True
                    continue
                if k not in source_item:
                    unique_dest = True
                    continue
                comparison = True
                match = False
            if comparison and match and not (unique_source and unique_dest):
                merge_dict(source_item, dest_item, merge_list_items)
                return
    elif source_item in destination:
        return
    destination.append(source_item)


def merge_dict(
    source: Dict[Any, Any], destination: Dict[Any, Any], merge_list_items: bool = True
) -> Dict[Any, Any]:
    """Merge two nested dict/list structures."""
    if not source:
        return destination
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            if node is None:
                destination[key] = value
            else:
                merge_dict(value, node, merge_list_items)
        elif isinstance(value, list):
            if key not in destination:
                destination[key] = []
            if isinstance(destination[key], list):
                for i in value:
                    merge_list_item(i, destination[key], merge_list_items)
        else:
            destination[key] = value
    return destination
