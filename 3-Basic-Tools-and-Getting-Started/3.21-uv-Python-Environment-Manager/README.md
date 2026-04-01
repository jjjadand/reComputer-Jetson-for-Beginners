# Install and Use `uv`

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## Introduction

`uv` is a fast Python package manager and virtual environment tool written in Rust. It can replace a combination of `pip`, `venv`, and parts of `pip-tools`, while being much faster on dependency resolution and environment setup.

## Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reload the shell if needed:

```bash
source ~/.bashrc
```

Confirm the installation:

```bash
uv --version
```

## Manage Python Versions

List available Python versions:

```bash
uv python list
```

Install a specific Python version:

```bash
uv python install 3.11
```

## Create a Virtual Environment

Create a virtual environment named `.venv`:

```bash
uv venv .venv --python 3.10
```

Activate it:

```bash
source .venv/bin/activate
```

## Manage Packages

Install packages:

```bash
uv pip install opencv-python
```

Install from `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

Uninstall a package:

```bash
uv pip uninstall requests
```

Export the current environment:

```bash
uv pip freeze > requirements.txt
```

## Suggested Next Steps

- Use `uv` with [OpenCV with CUDA](../3.8-OpenCV-with-CUDA/README.md) or other Python-based AI projects.
- Keep project dependencies isolated instead of installing everything into the system Python.

[Back to Module 3](../README.MD)
