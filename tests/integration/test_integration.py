# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

import filecmp
import os

from click.testing import CliRunner
import pytest
from ruamel import yaml

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


def test_validate_non_strict():
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data_non_strict/"
    schema_path = "tests/integration/fixtures/schema/schema.yaml"
    rules_path = "tests/integration/fixtures/rules/"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path,
            "-r",
            rules_path,
            "--non-strict",
            input_path,
        ],
    )
    assert result.exit_code == 0


def test_validate_vault():
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data_vault/"
    schema_path = "tests/integration/fixtures/schema/schema.yaml"
    os.environ["ANSIBLE_VAULT_ID"] = "dev"
    os.environ["ANSIBLE_VAULT_PASSWORD"] = "Password123"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path,
            input_path,
        ],
    )
    assert result.exit_code == 0


def test_validate_env(tmpdir):
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data_env/"
    schema_path = "tests/integration/fixtures/schema/schema.yaml"
    output_path = os.path.join(tmpdir, "output.yaml")
    os.environ["ABC"] = "DEF"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path,
            "-o",
            output_path,
            input_path,
        ],
    )
    assert result.exit_code == 0
    with open(output_path, "r") as file:
        data_yaml = file.read()
    y = yaml.YAML()
    data = y.load(data_yaml)
    assert data["root"]["children"][0]["name"] == "DEF"


def test_validate_empty_data():
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data_empty/"
    schema_path = "tests/integration/fixtures/schema/schema.yaml"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path,
            input_path,
        ],
    )
    assert result.exit_code == 0


def test_validate_additional_data():
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data/"
    input_path_2 = "tests/integration/fixtures/additional_data/"
    schema_path = "tests/integration/fixtures/additional_data_schema/schema.yaml"
    schema_path_fail = "tests/integration/fixtures/schema/schema.yaml"
    rules_path = "tests/integration/fixtures/rules/"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path,
            "-r",
            rules_path,
            input_path,
            input_path_2,
        ],
    )
    assert result.exit_code == 0
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-s",
            schema_path_fail,
            "-r",
            rules_path,
            input_path,
            input_path_2,
        ],
    )
    assert result.exit_code == 1


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


def test_validate_output(tmpdir):
    runner = CliRunner()
    input_path = "tests/integration/fixtures/data/"
    output_path = os.path.join(tmpdir, "output.yaml")
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-o",
            output_path,
            input_path,
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(output_path)


def test_merge(tmpdir):
    runner = CliRunner()
    input_path_1 = "tests/integration/fixtures/data_merge/file1.yaml"
    input_path_2 = "tests/integration/fixtures/data_merge/file2.yaml"
    output_path = os.path.join(tmpdir, "output.yaml")
    result_path = "tests/integration/fixtures/data_merge/result.yaml"
    result = runner.invoke(
        iac_validate.cli.main.main,
        [
            "-o",
            output_path,
            input_path_1,
            input_path_2,
        ],
    )
    assert result.exit_code == 0
    assert filecmp.cmp(output_path, result_path, shallow=False)
