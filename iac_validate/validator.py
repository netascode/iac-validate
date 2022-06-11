# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

import importlib.util
import logging
import os
import sys
from typing import List

import yamale
from yamale.yamale_error import YamaleError

from iac_validate import yaml

logger = logging.getLogger(__name__)


class Validator:
    def __init__(self, schema_path: str, rules_path: str):
        if schema_path:
            logger.info("Loading schema")
            self.schema = yamale.make_schema(schema_path, parser="ruamel")
        self.rules = {}
        if rules_path:
            logger.info("Loading rules")
            for filename in os.listdir(rules_path):
                if filename.endswith(".py"):
                    file_path = os.path.join(rules_path, filename)
                    spec = importlib.util.spec_from_file_location(
                        "iac_validate.rules", file_path
                    )
                    if spec is not None:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules["iac_validate.rules"] = mod
                        if spec.loader is not None:
                            spec.loader.exec_module(mod)
                            self.rules[mod.Rule.id] = mod.Rule

    def validate_syntax(self, input_paths: List[str]) -> bool:
        """Run syntactic validation"""

        def _validate_file(file_path: str) -> bool:
            error = False
            filename = os.path.basename(file_path)
            if os.path.isfile(file_path) and (
                ".yaml" in filename or ".yml" in filename
            ):
                logger.info("Validate file: %s", filename)
                data = yamale.make_data(file_path, parser="ruamel")
                try:
                    yamale.validate(self.schema, data, strict=True)
                except YamaleError as e:
                    error = True
                    logger.error(e.message.split("\n\t")[1])
            return error

        error = False
        for input_path in input_paths:
            if os.path.isfile(input_path):
                if _validate_file(input_path):
                    error = True
            else:
                for dir, subdir, files in os.walk(input_path):
                    for filename in files:
                        file_path = os.path.join(dir, filename)
                        if _validate_file(file_path):
                            error = True
        return error

    def validate_semantics(self, input_paths: List[str]) -> bool:
        """Run semantic validation"""
        error = False
        logger.info("Loading yaml files from %s", input_paths)
        data = yaml.load_yaml_files(input_paths)

        results = {}
        for rule in self.rules.values():
            logger.info("Verifying rule id %s", rule.id)
            paths = rule.match(data)
            if len(paths) > 0:
                results[rule.id] = paths
        if len(results) > 0:
            error = True
            for id, paths in results.items():
                logger.error(
                    "Rule {}: {} ({})".format(id, self.rules[id].description, paths)
                )
        return error
