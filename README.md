[![Tests](https://github.com/netascode/iac-validate/actions/workflows/test.yml/badge.svg)](https://github.com/netascode/iac-validate/actions/workflows/test.yml)
![Python Support](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-informational "Python Support: 3.10, 3.11, 3.12, 3.13")

# iac-validate

A CLI tool to perform syntactic and semantic validation of YAML files.

```
$ iac-validate -h
Usage: iac-validate [OPTIONS] [PATHS]...

  A CLI tool to perform syntactic and semantic validation of YAML files.

Options:
  --version              Show the version and exit.
  -v, --verbosity LVL    Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  -s, --schema FILE      Path to schema file. (optional, default:
                         '.schema.yaml', env: IAC_VALIDATE_SCHEMA)
  -r, --rules DIRECTORY  Path to semantic rules. (optional, default:
                         '.rules/', env: IAC_VALIDATE_RULES)
  -o, --output FILE      Write merged content from YAML files to a new YAML
                         file. (optional, env: IAC_VALIDATE_OUTPUT)
  --non-strict           Accept unexpected elements in YAML files.
  -h, --help             Show this message and exit.
```

Syntactic validation is done by basic YAML syntax validation (e.g., indentation) and by providing a [Yamale](https://github.com/23andMe/Yamale) schema and validating all YAML files against that schema. Semantic validation is done by providing a set of rules (implemented in Python) which are then validated against the YAML data. Every rule is implemented as a Python class and should be placed in a `.py` file located in the `--rules` path.

Each `.py` file must have a single class named `Rule`. This class must have the following attributes: `id`, `description` and `severity`. It must implement a `classmethod()` named `match` that has a single function argument `data` which is the data read from all YAML files. It should return a list of strings, one for each rule violation with a descriptive message. A sample rule can be found below.

```python
class Rule:
    id = "101"
    description = "Verify child naming restrictions"
    severity = "HIGH"

    @classmethod
    def match(cls, data):
        results = []
        try:
            for child in data["root"]["children"]:
                if child["name"] == "FORBIDDEN":
                    results.append("root.children.name" + " - " + str(child["name"]))
        except KeyError:
            pass
        return results
```

## Installation

Python 3.7+ is required to install `iac-validate`. Don't have Python 3.7 or later? See [Python 3 Installation & Setup Guide](https://realpython.com/installing-python/).

`iac-validate` can be installed in a virtual environment using `pip`:

```
pip install iac-validate
```

## Pre-Commit Hook

The tool can be integrated via a [pre-commit](https://pre-commit.com/) hook with the following config (`.pre-commit-config.yaml`), assuming the default values (`.schema.yaml`, `.rules/`) are appropriate:

```
repos:
  - repo: https://github.com/netascode/iac-validate
    rev: v0.1.6
    hooks:
      - id: iac-validate
```

In case the schema or validation rules are located somewhere else the required CLI arguments can be added like this:

```
repos:
  - repo: https://github.com/netascode/iac-validate
    rev: v0.1.6
    hooks:
      - id: iac-validate
        args:
          - '-s'
          - 'my_schema.yaml'
          - '-r'
          - 'rules/'
```

## Ansible Vault Support

Values can be encrypted using [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html). This requires Ansible (`ansible-vault` command) to be installed and the following two environment variables to be defined:

```
export ANSIBLE_VAULT_ID=dev
export ANSIBLE_VAULT_PASSWORD=Password123
```

`ANSIBLE_VAULT_ID` is optional, and if not defined will be omitted.

## Additional Tags

### Reading Environment Variables

The `!env` YAML tag can be used to read values from environment variables.

```yaml
root:
  name: !env VAR_NAME
```
