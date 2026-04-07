# Install and Use uv

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 15 Installation of uv environmental management tool

uv is a Python package management and virtual environment tool developed with Rust. Its objectives are very clear:

> It's not easy for Python to rely on management.

You can read uv as a combination of pip, venv, pip-tools.

### Install uv tools

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Upon installation, confirm:

```bash
uv --version
```

### Basic use

### Manage Python Versions

uv can easily manage several Python versions without additional tools such as pyenv.

View available Python versions:

```bash
uv python list
```

> The uv python command 3.11 can install a specific version of Python.

### Create virtual environments

```bash
uv venv .opencv --python 3.10.12
```

Of which .opencv is the name of the virtual environment; 3.10.12 is a python version of the virtual environment.

### Activate Virtual Environment

```bash
source .venv/bin/activate
```

### Package management

```bash
# Install new packages:
uv pip install opencv-python
# uv pip install -r requirements.txt

# Uninstall packages:
uv pip uninstall requests

# Export the dependencies of the current environment
uv pip freeze > requirements.txt
```

[Back to Module 3](../README.MD)
