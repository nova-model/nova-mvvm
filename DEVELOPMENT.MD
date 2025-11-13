# Development Guide

This document provides guidelines and instructions for setting up and contributing to
the MVVM Library for Python project.

## Starting from the template

- Add other Python dependencies you project need with [`Pixi add`](https://pixi.sh/dev/reference/cli/pixi/add/#pixi-add).
- Modify Dockerfile as needed. Please make sure it can still run as non-root (we use it in GitHub Actions and in general this
is a good practice).
- install pre-commit (if not already installed) - `pixi run pre-commit install`
- finally, clear the content of this section and add the description of your project. You can keep/adjust instructions
below

Note 1: please don't change linter settings, license, code of conduct without discussing with the team first - we want to keep them
the same for all our projects.

Note 2: if you think some changes that you've made might be useful for other projects as well, please fill free
to create an issue [in this repo](https://code.ornl.gov/ndip/project-templates/python/-/issues/new)


## Installation

```commandline
pixi install
```

## Running
### From source
```bash
pixi run app
```

### Using Docker
```bash
# build from source
docker build -f dockerfiles/Dockerfile -t nova-mvvm .
# run a container
docker run nova-mvvm
```

## Formatting
```commandline
pixi run ruff format
```

## Linting
```commandline
pixi run ruff check
pixi run mypy .
```

## Testing
```commandline
pixi run pytest
```
or, with coverage
```commandline
pixi run coverage run
pixi run coverage report
```

## Updating project from template

This project was created from a [template](https://code.ornl.gov/ndip/project-templates/python.git) using [copier](https://copier.readthedocs.io/). If the template has changed, you
can try to update the project to incorporate these changes. Just enter the project folder, make sure `git status`
shows it clean, and run:
```
copier update
```
See [here](https://copier.readthedocs.io/en/stable/updating/#updating-a-project) for more information.


## CI/CD in GitHub

Take a look at the [`.github/workflows`](.github/workflows) folder.
Actions to lint and test your code will run automatically on each commit.
The action for building and releasing this package needs to be triggered manually.

### Versioning

The "source of truth" for the version number is in the [`pyproject.toml`](pyproject.toml) file. It is used for Docker
image tags, python package versioning, and automatic creation of git tags.

### Publishing docs to readthedocs.io

This repo has a [webhook](https://github.com/nova-model/nova-mvvm/settings/hooks) that automatically triggers documentation builds on readthedocs.
