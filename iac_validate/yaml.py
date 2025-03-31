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
    result = deduplicate_list_items(result)
    return result


def merge_list_item(source_item: Any, destination: List[Any]) -> None:
    """Merge item into list."""
    if isinstance(source_item, dict):
        # check if we have an item in destination with matching primitives
        for dest_item in destination:
            match = True
            comparison = False
            for k, v in source_item.items():
                if isinstance(v, dict) or isinstance(v, list) or k not in dest_item:
                    continue
                comparison = True
                if v != dest_item[k]:
                    match = False
            for k, v in dest_item.items():
                if isinstance(v, dict) or isinstance(v, list) or k not in source_item:
                    continue
                comparison = True
                if v != source_item[k]:
                    match = False
            if comparison and match:
                merge_dict(source_item, dest_item)
                return
    destination.append(source_item)


def merge_dict(source: Dict[Any, Any], destination: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge two nested dict/list structures."""
    if not source:
        return destination
    for key, value in source.items():
        if key not in destination:
            destination[key] = value
        elif isinstance(value, dict):
            if isinstance(destination[key], dict):
                merge_dict(value, destination[key])
        elif isinstance(value, list):
            if isinstance(destination[key], list):
                destination[key] += value
        else:
            destination[key] = value
    return destination


def deduplicate_list_items(data: Dict[Any, Any]) -> Dict[Any, Any]:
    """Deduplicate list items."""
    for key, value in data.items():
        if isinstance(value, dict):
            deduplicate_list_items(value)
        elif isinstance(value, list):
            deduplicated_list: List[Any] = []
            for i in value:
                merge_list_item(i, deduplicated_list)
            for i in deduplicated_list:
                if isinstance(i, dict):
                    deduplicate_list_items(i)
            data[key] = deduplicated_list
    return data
