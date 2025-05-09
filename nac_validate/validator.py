# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

import importlib
import importlib.util
import logging
import warnings
import os
import sys
from typing import Any
from pathlib import Path

import typer
from ruamel import yaml
import yamale
from yamale.yamale_error import YamaleError
from inspect import signature

from .cli.defaults import DEFAULT_SCHEMA, DEFAULT_RULES
from nac_yaml.yaml import write_yaml_file, load_yaml_files

logger = logging.getLogger(__name__)


class Validator:
    def __init__(self, schema_path: Path, rules_path: Path):
        self.data: dict[str, Any] | None = None
        self.schema = None
        if os.path.exists(schema_path):
            logger.info("Loading schema")
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    action="ignore",
                    category=SyntaxWarning,
                    message="invalid escape sequence",
                )
                self.schema = yamale.make_schema(schema_path, parser="ruamel")
        elif schema_path == DEFAULT_SCHEMA:
            logger.info("No schema file found")
        else:
            logger.error("Schema file not found: {}".format(schema_path))
            raise typer.Exit(1)
        self.errors: list[str] = []
        self.rules = {}
        if os.path.exists(rules_path):
            logger.info("Loading rules")
            for filename in os.listdir(rules_path):
                if Path(filename).suffix == ".py":
                    try:
                        file_path = Path(rules_path, filename)
                        spec = importlib.util.spec_from_file_location(
                            "nac_validate.rules", file_path
                        )
                        if spec is not None:
                            mod = importlib.util.module_from_spec(spec)
                            sys.modules["nac_validate.rules"] = mod
                            if spec.loader is not None:
                                spec.loader.exec_module(mod)
                                self.rules[mod.Rule.id] = mod.Rule
                    except:  # noqa: E722
                        logger.error("Failed loading rule: {}".format(filename))
        elif rules_path == DEFAULT_RULES:
            logger.info("No rules found")
        else:
            logger.error("Rules directory not found: {}".format(rules_path))
            raise typer.Exit(1)

    def _validate_syntax_file(self, file_path: Path, strict: bool = True) -> None:
        """Run syntactic validation for a single file"""
        if os.path.isfile(file_path) and file_path.suffix in [".yaml", ".yml"]:
            logger.info("Validate file: %s", file_path)

            # YAML syntax validation
            data = None
            try:
                data = load_yaml_files([file_path])
            except yaml.error.MarkedYAMLError as e:
                line = 0
                column = 0
                if e.problem_mark is not None:
                    line = e.problem_mark.line + 1
                    column = e.problem_mark.column + 1
                msg = "Syntax error '{}': Line {}, Column {} - {}".format(
                    file_path,
                    line,
                    column,
                    e.problem,
                )
                logger.error(msg)
                self.errors.append(msg)
                return

            # Schema syntax validation
            if self.schema is None or data is None:
                return
            try:
                yamale.validate(self.schema, [(data, file_path)], strict=strict)
            except YamaleError as e:
                for result in e.results:
                    for err in result.errors:
                        msg = "Syntax error '{}': {}".format(result.data, err)
                        logger.error(msg)
                        self.errors.append(msg)

    def validate_syntax(self, input_paths: list[Path], strict: bool = True) -> bool:
        """Run syntactic validation"""
        for input_path in input_paths:
            if os.path.isfile(input_path):
                self._validate_syntax_file(input_path, strict)
            else:
                for dir, subdir, files in os.walk(input_path):
                    for filename in files:
                        file_path = Path(dir, filename)
                        self._validate_syntax_file(file_path, strict)
        if self.errors:
            return True
        return False

    def validate_semantics(self, input_paths: list[Path]) -> bool:
        """Run semantic validation"""
        if not self.rules:
            return False

        error = False
        logger.info("Loading yaml files from %s", input_paths)
        if self.data is None:
            self.data = load_yaml_files(input_paths)

        results = {}
        for rule in self.rules.values():
            logger.info("Verifying rule id %s", rule.id)
            sig = signature(rule.match)
            if len(sig.parameters) == 1:
                paths = rule.match(self.data)
            elif len(sig.parameters) == 2:
                paths = rule.match(self.data, self.schema)
            if len(paths) > 0:
                results[rule.id] = paths
        if len(results) > 0:
            error = True
            for id, paths in results.items():
                msg = "Semantic error, rule {}: {} ({})".format(
                    id, self.rules[id].description, paths
                )
                logger.error(msg)
                self.errors.append(msg)
        return error

    def write_output(self, input_paths: list[Path], path: Path) -> None:
        if self.data is None:
            self.data = load_yaml_files(input_paths)
        write_yaml_file(self.data, path)
