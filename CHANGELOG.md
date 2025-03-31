# 0.2.8 (unreleased)

- BREAKING CHANGE: Update YAML merge logic to merge list items with matching attributes and primitive values, even if both have additional attributes the other does not have

# 0.2.7

- Suppress Yamale syntax warnings when running Python 3.12+

# 0.2.6

- Fix issue with directly nested lists in YAML files

# 0.2.5

- Check non-default schema and rules paths for existence

# 0.2.4

- Dependency updates

# 0.2.3

- Handle file errors gracefully
- Allow empty YAML files

# 0.2.2

- Add `--non-strict` CLI argument to accept unexpected elements in YAML files

# 0.2.1

- Do not merge YAML dictionary list items, where each list item has unique attributes with primitive values

# 0.2.0

- Preserve YAML quotes in output
- Add `!env` tag to read values from environment variables

# 0.1.8

- Use `ruamel.yaml` package consistently

# 0.1.7

- Add `output` CLI argument

# 0.1.6

- Add YAML syntax validation

# 0.1.5

- Add pre-commit config

# 0.1.4

- Add support for logging multiple error messsages

# 0.1.3

- Add support for Ansible Vault encrypted values

# 0.1.2

- Allow multiple paths as argument

# 0.1.1

- No changes

# 0.1.0

- Initial release
