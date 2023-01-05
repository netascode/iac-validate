# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

import logging
import sys
from typing import List

import click
import errorhandler

import iac_validate.validator

from . import options

logger = logging.getLogger(__name__)

error_handler = errorhandler.ErrorHandler()


def configure_logging(level: str) -> None:
    if level == "DEBUG":
        lev = logging.DEBUG
    elif level == "INFO":
        lev = logging.INFO
    elif level == "WARNING":
        lev = logging.WARNING
    elif level == "ERROR":
        lev = logging.ERROR
    else:
        lev = logging.CRITICAL
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(lev)
    error_handler.reset()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(iac_validate.__version__)
@click.option(
    "-v",
    "--verbosity",
    metavar="LVL",
    is_eager=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
    help="Either CRITICAL, ERROR, WARNING, INFO or DEBUG",
    default="WARNING",
)
@options.paths
@options.schema
@options.rules
@options.output
@options.non_strict
def main(
    verbosity: str,
    paths: List[str],
    schema: str,
    rules: str,
    output: str,
    non_strict: bool,
) -> None:
    """A CLI tool to perform syntactic and semantic validation of YAML files."""
    configure_logging(verbosity)

    validator = iac_validate.validator.Validator(schema, rules)
    error = validator.validate_syntax(paths, not non_strict)
    if error:
        exit()
    validator.validate_semantics(paths)
    if output:
        validator.write_output(paths, output)
    exit()


def exit() -> None:
    if error_handler.fired:
        sys.exit(1)
    else:
        sys.exit(0)
