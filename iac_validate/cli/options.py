# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

import click

DEFAULT_SCHEMA = ".schema.yaml"
DEFAULT_RULES = ".rules/"

rules = click.option(
    "-r",
    "--rules",
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    envvar="IAC_VALIDATE_RULES",
    default=DEFAULT_RULES,
    help="Path to semantic rules. (optional, default: '.rules/', env: IAC_VALIDATE_RULES)",
    required=False,
)

schema = click.option(
    "-s",
    "--schema",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
    envvar="IAC_VALIDATE_SCHEMA",
    default=DEFAULT_SCHEMA,
    help="Path to schema file. (optional, default: '.schema.yaml', env: IAC_VALIDATE_SCHEMA)",
    required=False,
)

output = click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, dir_okay=False, file_okay=True),
    envvar="IAC_VALIDATE_OUTPUT",
    help="Write merged content from YAML files to a new YAML file. (optional, env: IAC_VALIDATE_OUTPUT)",
    required=False,
)

non_strict = click.option(
    "--non-strict",
    is_flag=True,
    help="Accept unexpected elements in YAML files.",
)

paths = click.argument(
    "paths",
    type=click.Path(exists=True, dir_okay=True, file_okay=True),
    nargs=-1,
)
