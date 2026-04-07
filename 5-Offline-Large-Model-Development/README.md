# Offline Large Model Development

This module merges `xiaobai-lesson` Chapter 12 into the `reComputer-Jetson-for-Beginners` course structure. The original material focused on running local large models on Jetson with Ollama, Open WebUI, offline ASR/TTS, and multimodal agent-style applications.

## What You Will Learn

- How to prepare a local LLM runtime on Jetson with Ollama
- How to expose local models through a browser UI such as Open WebUI
- How to compare and run several offline text LLMs
- How to run vision-language models for image understanding tasks
- How to wire ASR, TTS, and local LLM inference into a voice pipeline
- How multimodal voice assistants, table understanding, visual analysis, and autonomous agents fit together

## Module 5 Structure

| **Chapter** | **Content** |
|:-----------:|:------------|
| Module 5.1 | [Environment and Basics with Ollama](./5.1-Environment-and-Basics-Ollama/README.md) |
| Module 5.2 | [Offline Text LLMs](./5.2-Offline-Text-LLMs/README.md) |
| Module 5.3 | [Offline Vision-Language Models and Applications](./5.3-Offline-Vision-Language-Models-and-Applications/README.md) |
| Module 5.4 | [Offline Speech Pipeline Basics](./5.4-Offline-Speech-Pipeline-Basics/README.md) |
| Module 5.5 | [Offline Multimodal Voice Applications](./5.5-Offline-Multimodal-Voice-Applications/README.md) |

## Suggested Learning Order

1. Set up the runtime in Module 5.1.
2. Validate text-only models in Module 5.2.
3. Move to vision-language models in Module 5.3.
4. Add offline ASR and TTS in Module 5.4.
5. Build full assistant-style workflows in Module 5.5.

## Practical Notes

- Most examples in the merged source assume JetPack 6.2 and an Ollama-based local runtime.
- Some multimodal and voice workflows are too heavy for smaller Jetson SKUs, especially 4 GB variants.
- The source materials often refer to the Seeed workspace path `/opt/seeed/development_guide/12_llm_offline/seeed_ws`; keep that in mind if you are using the prebuilt Seeed image.
