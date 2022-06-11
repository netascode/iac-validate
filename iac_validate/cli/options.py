# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

import click

rules = click.option(
    "-r",
    "--rules",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Path to semantic rules.",
    required=False,
)

schema = click.option(
    "-s",
    "--schema",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="Path to schema file.",
    required=False,
)

path = click.argument(
    "path",
    type=click.Path(exists=True, dir_okay=True, file_okay=True),
    nargs=-1,
)
