# Environment and Basics with Ollama

This subchapter merges the Ollama and local-runtime setup material from `xiaobai-lesson` Chapter 12.

## Why Ollama on Jetson

The source material used Ollama as the default offline LLM runtime because it provides:

- simple local model download and execution
- a straightforward CLI
- a local HTTP API
- OpenAI-compatible integration patterns for surrounding tools

## Basic Requirements

- Jetson device running JetPack 6.2
- enough storage for models and caches
- a terminal environment with `curl` available

Some Seeed Jetson images already ship with Ollama preinstalled. Check first:

```bash
ollama --version
```

## Install Ollama

```bash
sudo apt install -y curl
curl -fsSL https://ollama.com/install.sh | sh
```

Check that it is available:

```bash
ollama --help
ollama list
```

## Core Ollama Commands

| Command | Purpose |
| --- | --- |
| `ollama run <model>` | Run a model locally |
| `ollama pull <model>` | Download a model |
| `ollama list` | Show downloaded models |
| `ollama ps` | Show active model processes |
| `ollama rm <model>` | Remove a model |
| `ollama serve` | Start the local service explicitly when needed |

## Install Open WebUI

The source material paired Ollama with Open WebUI so Jetson users could access local models through a browser-based chat interface.

Pull the image:

```bash
docker pull ghcr.io/open-webui/open-webui:main
```

Run it:

```bash
mkdir -p /opt/seeed/development_guide/12_llm_offline/open-webui/data

docker run -d --restart always --name open-webui \
  --network host \
  -v /opt/seeed/development_guide/12_llm_offline/open-webui/data:/app/backend/data \
  -e OLLAMA_BASE_URL=http://127.0.0.1:11434 \
  ghcr.io/open-webui/open-webui:main
```

Inspect logs:

```bash
docker logs -f open-webui
```

Open it locally with:

```text
http://localhost:8080
```

From another device on the same LAN, replace `localhost` with the Jetson IP address.

## Supporting Desktop Setup

The source chapter grouped two extra setup items with the base environment:

- switch to a Chinese input method if you need Chinese prompts or search terms
- keep Docker working, because Open WebUI and some other local frontends rely on it

If you are using the prebuilt course image, those pieces may already be present.

## Practical Advice

- Start with a small model first so you can validate the runtime before downloading heavier checkpoints.
- Keep Ollama and Open WebUI on the same machine during initial setup to simplify networking.
- Use the browser UI only after `ollama run` works from the terminal.
