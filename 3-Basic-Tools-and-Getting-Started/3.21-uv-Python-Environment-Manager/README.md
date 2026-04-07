# Install and Use uv

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## 15安装uv环境管理工具

uv是一个用Rust编写的Python包管理和虚拟环境工具。它的目标非常明确：

```
让 Python 的依赖管理又快又省心。
```

你可以把uv理解为：pip（安装包）、venv（虚拟环境）、pip-tools（依赖锁定）这三者的合体升级版。

### 安装uv工具

在jetson设备的终端窗口中运行下面的命令安装uv：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装完成后，确认：

```bash
uv --version
```

### 基础使用

### 管理Python版本

uv可以轻松管理多个Python版本，无需额外安装pyenv等工具。

查看可用的Python版本：

```bash
uv python list
```

```
使用 uv python install 3.11 命令可以安装特定版本的 Python.
```

### 创建虚拟环境

```bash
uv venv .opencv --python 3.10.12
```

其中.opencv是虚拟环境的名称；3.10.12是虚拟环境中python的版本。

### 激活虚拟环境

```bash
source .venv/bin/activate
```

### 包管理

```bash
# 安装新的包:
uv pip install opencv-python
# uv pip install -r requirements.txt
# 卸载包：
uv pip uninstall requests
# 导出当前环境的依赖
uv pip freeze > requirements.txt
```

[Back to Module 3](../README.MD)
