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


def compare_dict(source: Dict[Any, Any], destination: Dict[Any, Any]) -> int:
    """Compare two nested dict structures.

    :returns: '0' if the two dicts are not equal, '1' if there are no matching keys, '2' if the dicts are equal
    """
    if not source:
        return destination == source
    comparison = False
    for key, value in source.items():
        if key not in destination or isinstance(value, list):
            continue
        if isinstance(value, dict):
            if compare_dict(value, destination[key]) == 0:
                return 0
        elif value != destination[key]:
            return 0
        comparison = True
    if comparison:
        return 2
    return 1


def merge_list_item(
    source_item: Any, destination: List[Any], merge_list_items: bool = True
) -> None:
    """Merge item into list."""
    if isinstance(source_item, dict):
        if merge_list_items:
            # check if we have a matching item in destination
            for dest_item in destination:
                if compare_dict(source_item, dest_item) == 2:
                    merge_dict(source_item, dest_item, merge_list_items)
                    return
            destination.append(merge_dict(source_item, {}, merge_list_items))
        else:
            destination.append(source_item)
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
                merge_dict(value, node)
        elif isinstance(value, list):
            node = destination.setdefault(key, [])
            if node is None:
                destination[key] = value
            else:
                destination[key].extend(value)
            # new_list = []
            # for i in destination.get(key, []):
            #     merge_list_item(i, new_list, merge_list_items)
            # for i in value:
            #     merge_list_item(i, new_list, merge_list_items)
            # destination[key] = new_list
            # if key not in destination:
            #     destination[key] = []
            # if isinstance(destination[key], list):
            #     for i in value:
            #         merge_list_item(i, destination[key], merge_list_items)

            # deduplicate list
            new_list = []
            for i in value:
                merge_list_item(i, new_list, merge_list_items)
            destination[key] = new_list
        else:
            destination[key] = value
    return destination
