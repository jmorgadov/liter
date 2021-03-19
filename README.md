# liter

Tool for automating basic python packages task.

## Installation

```shell
pip install liter
```

## Features

- Changelog autogeneration based on git history.
- Changing project version recursively
  
## How to use

### Generating changelogs

It will separate the project versions according to the version tags added on git.

To generate a basic `CHANGELOG.md` file type:

```shell
liter changelog
```

If you want the changelog to start at a specific version type:

```shell
liter changelog --start-in [VERSION]
```

Example:

```shell
liter changelog --start-in 0.2.0
```

### Changing version

Changing version with **liter** will find all the files in your project recursively where your current package version is written. For each line in every file where a version match is found you can choose if modify the line or not.

To change project version type:

```shell
liter version
```

Which is the same as:

```shell
liter version patch
```

To upgrade another version number type:

```shell
liter version minor
```

or:

```shell
liter version major
```

Where `major`, `minor` and `patch` refers to the 1st, 2nd and 3rd version numbers respectively. (See [Semantic Versioning](https://semver.org/) for mor information).

## Liter config file

When runing any command in **liter** a `literconfig.json` file will be created with some default configuraions. You can customize this parameters as you want.

### Config parameters

- `version`

    This is your current package version. By default **liter** will look for a `setup.py` or a `pyproject.toml` to find your current version. If you do not have any of this file you must change the `version` parameter in `literconfig.json` to your current package version.

- `version_ignore`

    List of patters to ignore when searching a version match in files.

- `changelog_sections`

    Sections that will be included in changelog file. Each key, value pair represents the section names and a list of *key words* respectively. A commit will be added to a section if the first word of the commit is any of the sections defined *key word*.

- `changelog_include_others`

    Wheter to include or not the `Others` section in changelogs. The `Other` sections contains all the commits that did not match with any of the *key words* added in any section of `changelog_sections`.

- `changelog_ignore_commits`

    All the commits that match with any of these *key words* will not be included in the changelog file.

- `changelog_only_path_pattern`

    Only include commits that affected files which path contains any of the patterns specified.
