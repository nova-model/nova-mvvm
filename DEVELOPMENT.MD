# Development Guide

This document provides guidelines and instructions for setting up and contributing to
the MVVM Library for Python project.

## Installation
```commandline
pip install poetry
poetry install --no-root
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
