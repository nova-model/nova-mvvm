MVVM Library for Python
=======================

# Introduction

`nova-mvvm` is a Python package designed to simplify the implementation of the Model-View-ViewModel (MVVM) pattern.
It provides data-binding abstractions for PyQt5, PyQt6,
[Trame](https://github.com/Kitware/trame), and [Panel](https://github.com/holoviz/panel) applications.

## Installation

```bash
pip install nova-mvvm
```

See the [documentation](https://nova-application-development.readthedocs.io/projects/mvvm-lib/en/latest/)
for concepts, examples, and the API reference.

## Compatibility

Version 1.x supports Python 3.10 through 3.13. The documented API follows semantic versioning:
breaking changes require a new major release, while names under `nova.mvvm._internal` are not public API.

See the [changelog](https://github.com/nova-sdk/nova-mvvm/blob/main/CHANGELOG.md)
for release notes and migration information.
