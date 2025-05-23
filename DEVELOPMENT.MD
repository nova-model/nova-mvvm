# Development Guide

This document provides guidelines and instructions for setting up and contributing to
the MVVM Library for Python project.

## Starting from the template

- Add other Python dependencies you project need with `poetry add xxx` or `poetry add --dev xxx`
- Modify Dockerfile as needed. Please make sure it can still run as non-root (we use it in GitLab CI/CD and in general this
is a good practice).
- install pre-commit (if not already installed) - `pip install pre-commit`
- activate `pre-commit` for your project: `cd <project folder> && pre-commit install`
- finally, clear the content of this section and add the description of your project. You can keep/adjust instructions
below

Note 1: please don't change linter settings, license, code of conduct without discussing with the team first - we want to keep them
the same for all our projects.

Note 2: if you think some changes that you've made might be useful for other projects as well, please fill free
to create an issue [in this repo](https://code.ornl.gov/ndip/project-templates/python/-/issues/new)


## Installation

```commandline
pip install poetry

poetry install
```

## Running
### From source
```bash
poetry run app
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
poetry run ruff format
```

## Linting
```commandline
poetry run ruff check
poetry run mypy .
```

## Testing
```commandline
poetry run pytest
```
or, with coverage
```commandline
poetry run coverage run
poetry run coverage report
```

## Updating project from template

This project was created from a [template](https://code.ornl.gov/ndip/project-templates/python.git) using [copier](https://copier.readthedocs.io/). If the template has changed, you
can try to update the project to incorporate these changes. Just enter the project folder, make sure `git status`
shows it clean, and run:
```
poetry run copier update
```
See [here](https://copier.readthedocs.io/en/stable/updating/#updating-a-project) for more information.


## CI/CD in GitLab

Take a look at the [`.gitlab-ci.yml`](.gitlab-ci.yml) file. It configures pipelines to run in GitLab.
Some jobs will run automatically on each commit, jobs to
build packages and Docker images need to be triggered manually.


### Versioning

The "source of truth" for the version number is in the [`pyproject.toml`](pyproject.toml) file. It is used for Docker
image tags, python package versioning, and automatic creation of git tags.
### Publishing docs to readthedocs.io

The  [`.gitlab-ci.yml`](.gitlab-ci.yml) file contains a job to publish documentation to readthedocs.io. This job requires
two environment variables _READTHEDOCS_WEBHOOK_URL_ and _READTHEDOCS_WEBHOOK_SECRET_ to be available. You should get
the URL and the secret from your readthedocs project (_click on your project, or create a new one ->admin->Integrations->Generic API incoming webhook_)
and save them in GitLab (_Gitlab project->Settings->CI/CD->Variables->Add variable_).
