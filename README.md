[![Tests](https://github.com/netascode/iac-validate/actions/workflows/test.yml/badge.svg)](https://github.com/netascode/iac-validate/actions/workflows/test.yml)
![Python Support](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-informational "Python Support: 3.6, 3.7, 3.8, 3.9, 3.10")

# iac-validate

A CLI tool to perform syntactic and semantic validation of YAML files.

```shell
$ iac-validate -h
Usage: iac-validate [OPTIONS] PATH

  A CLI tool to perform syntactic and semantic validation of YAML files.

Options:
  --version              Show the version and exit.
  -v, --verbosity LVL    Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  -s, --schema FILE      Path to schema file.
  -r, --rules DIRECTORY  Path to semantic rules.
  -h, --help             Show this message and exit.
```

Syntactic validation is done by providing a [Yamale](https://github.com/23andMe/Yamale) schema and validating all YAML files against that schema. Semantic validation is done by providing a set of rules (implemented in Python) which are then validated against the YAML data. Every rule is implemented as a Python class and should be placed in a `.py` file located in the `--rules` path.

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

Python 3.6+ is required to install `iac-validate`. Don't have Python 3.6 or later? See [Python 3 Installation & Setup Guide](https://realpython.com/installing-python/).

`iac-validate` can be installed in a virtual environment using `pip`:

```shell
pip install iac-validate
```
