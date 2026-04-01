# Docker on Jetson

[Back to Module 3](../README.MD) | [Back to Table of Contents](../../Table-of-Contents.md)

## Introduction

Docker is a practical way to package applications and their dependencies into portable containers. On Jetson, containers are especially useful for AI development because they let you isolate Python environments, reuse prebuilt images, and run GPU-accelerated workloads without changing the host system too much.

This page introduces Docker on Jetson with beginner-friendly installation, image management, and container workflow examples.

## Install Docker Engine

Update the package index and install the required dependencies:

```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common
```

Add the official Docker GPG key:

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

Add the Docker repository:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install Docker:

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Check the installation:

```bash
docker --version
sudo systemctl status docker
```

## Install NVIDIA Container Toolkit

To let Docker containers access Jetson GPU resources, install NVIDIA Container Toolkit:

```bash
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)

curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

Install and configure it:

```bash
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

## Test GPU Access in a Container

On Jetson, `nvidia-smi` is usually not available like it is on desktop GPUs, so a more reliable validation method is to start an L4T container and inspect the mounted CUDA stack:

```bash
sudo docker run --rm --runtime=nvidia --network host \
  nvcr.io/nvidia/l4t-base:r36.4.0 \
  bash -lc 'ls /usr/local/cuda && cat /etc/nv_tegra_release'
```

> Note: Choose an `l4t-base` tag that matches your JetPack and L4T version. If the tag does not match your system, pull a compatible one first.

You can also open [Jtop and System Monitoring](../3.16-Jtop-and-System-Monitoring/README.md) on the host while running a GPU-enabled container to confirm GPU activity.

## Allow Non-Root Docker Usage

To avoid typing `sudo` every time:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

After re-login or opening a new shell, test with:

```bash
docker ps
```

## Common Docker Commands

### Pull an Image

```bash
docker pull ultralytics/ultralytics:8.3.201-jetson-jetpack6
```

List local images:

```bash
docker image ls
```

### Start an Interactive Container

```bash
docker run --runtime=nvidia -it --rm --network host \
  ultralytics/ultralytics:8.3.201-jetson-jetpack6
```

Meaning of the main options:

| Option | Description |
| --- | --- |
| `--runtime=nvidia` | Enables GPU access inside the container |
| `-it` | Starts the container in interactive terminal mode |
| `--rm` | Deletes the container after exit |
| `--network host` | Reuses the host network stack |

### View Running Containers

```bash
docker ps
docker ps -a
```

### Run a Container in the Background

```bash
docker run -d --name jetson-demo --runtime=nvidia --network host \
  ultralytics/ultralytics:8.3.201-jetson-jetpack6 sleep infinity
```

Enter it later with:

```bash
docker exec -it jetson-demo bash
```

## Transfer Files Between Host and Container

Copy a host file into a container:

```bash
docker cp ./test_file.txt jetson-demo:/workspace/
```

Copy a file from the container back to the host:

```bash
docker cp jetson-demo:/workspace/output.txt /home/seeed/
```

For larger projects, bind mounts are usually more convenient than repeated `docker cp`:

```bash
docker run --runtime=nvidia -it --rm --network host \
  -v /home/seeed/project:/workspace/project \
  ultralytics/ultralytics:8.3.201-jetson-jetpack6
```

## Save, Load, and Reuse Images

### Commit a Container as a New Image

```bash
docker commit jetson-demo my_container:latest
```

### Export an Image to a Tar File

```bash
docker save -o my_container.tar my_container:latest
```

### Import an Image from a Tar File

```bash
docker load -i my_container.tar
```

### Push an Image to Docker Hub

```bash
docker login -u <your-dockerhub-username>
docker tag my_container:latest <your-dockerhub-username>/my_container:latest
docker push <your-dockerhub-username>/my_container:latest
```

### Remove an Image

```bash
docker rmi my_container:latest
```

## Troubleshooting

- If `docker pull` is slow or fails, verify the Jetson network connection in [Network and Wi-Fi](../3.12-Network-and-Wi-Fi/README.md).
- If `docker: permission denied` appears, re-open the shell after adding your user to the `docker` group.
- If GPU access fails inside the container, check whether NVIDIA Container Toolkit is installed and whether the image tag matches your JetPack release.
- If a service inside the container needs to be opened from another PC, use `--network host` or map the port explicitly with `-p`.

## Suggested Next Steps

- Use [SSH Remote Access](../3.13-SSH-Remote-Access/README.md) or [VS Code](../3.19-VS-Code/README.md) to manage Jetson containers remotely.
- Use [JupyterLab](../3.20-JupyterLab/README.md) inside a container if you want an isolated Python workflow.
- Use [uv Python Environment Manager](../3.21-uv-Python-Environment-Manager/README.md) when Docker is too heavy and you only need per-project Python isolation.

## Reference

- [Docker Guides](https://docs.docker.com/guides/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/)

[Back to Module 3](../README.MD)
