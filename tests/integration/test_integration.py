# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

from click.testing import CliRunner
import pytest

import iac_validate.cli.main

pytestmark = pytest.mark.integration


def test_validate():
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data/"
    schema_path = "tests/integration/fixtures/schema/schema.yaml"
    rules_path = "tests/integration/fixtures/rules/"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path,
            "-r",
            rules_path,
            input_path,
        ],
    )
    assert result.exit_code == 0


def test_validate_syntax():
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data_syntax_error/"
    schema_path = "tests/integration/fixtures/schema/schema.yaml"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path,
            input_path,
        ],
    )
    assert result.exit_code == 1


def test_validate_semantics():
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data_semantic_error/"
    rules_path = "tests/integration/fixtures/rules/"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-r",
            rules_path,
            input_path,
        ],
    )
    assert result.exit_code == 1
