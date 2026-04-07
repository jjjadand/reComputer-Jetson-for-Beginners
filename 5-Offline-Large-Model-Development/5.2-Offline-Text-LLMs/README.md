# Offline Text LLMs

This subchapter merges the text-only model lineup from `xiaobai-lesson` Chapter 12.

## General Workflow

For all text-only models in the source material, the usage pattern is the same:

```bash
ollama run <model-name>
```

If the model is not already local, Ollama downloads it first and then starts an interactive session.

Exit a session with `Ctrl + D`.

## Model Lineup from the Source Chapter

### Llama 3.2

The source positioned `llama3.2:3b` as a practical local baseline:

```bash
ollama run llama3.2:3b
```

Good fit:

- lightweight general chat
- quick local experiments
- low-friction first-run validation

### Qwen3

The source used `qwen3:8b` as a stronger multilingual and reasoning-oriented text model:

```bash
ollama run qwen3:8b
```

Good fit:

- multilingual chat
- stronger reasoning than smaller entry-level models
- code and structured instructions

### Phi-4-mini

The merged source used `phi4-mini:3.8b`:

```bash
ollama run phi4-mini:3.8b
```

Good fit:

- smaller local footprint
- efficient general-purpose chat
- devices with tighter memory limits

### DeepSeek-R1

The merged source included DeepSeek-R1 for reasoning-heavy workflows:

```bash
ollama run deepseek-r1
```

Good fit:

- logic-heavy prompts
- coding-style reasoning
- exploration of reasoning-first models

## How to Compare Them on Jetson

A simple practical comparison loop is:

1. Run the same prompt on multiple models.
2. Measure startup time and first-token delay.
3. Watch RAM and swap pressure.
4. Judge whether the quality gain is worth the extra latency.

Example prompts:

```text
Explain ROS2 topics vs services in simple terms.
Write a Python script to read a USB camera and save one frame.
Summarize the steps to install Open WebUI on Jetson.
```

## Practical Advice

- Start with the smallest model that satisfies your task.
- Use Qwen or DeepSeek when reasoning quality matters more than startup speed.
- Use Phi or Llama when you need a lighter local assistant.
- Keep notes on which models work well on your exact Jetson SKU, because the usable model size changes a lot between 4 GB, 8 GB, and larger systems.
