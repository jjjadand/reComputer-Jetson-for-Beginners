# Offline Vision-Language Models and Applications

This subchapter merges the vision-language and multimodal application lessons from `xiaobai-lesson` Chapter 12.

## Supported Model Examples from the Source

The merged source covered four offline multimodal models exposed through Ollama:

- `qwen2.5vl:3b`
- `gemma3:4b`
- `llava:7b`
- `minicpm-v:8b`

Each model follows the same basic usage pattern:

```bash
ollama run qwen2.5vl:3b
```

Inside the interactive prompt, the source used image-path prompts like:

```text
What do you see in this picture? :./test.png
```

## What These Models Are Good At

- image description
- question answering over a single image
- OCR-style extraction from screenshots and documents
- scene understanding for robotics tasks
- basic video or sequence reasoning when wrapped by higher-level tooling

## Visual Understanding Application

The source chapter used a `ToolsManager -> model interface` pattern. The core flow was:

1. capture a frame
2. build a prompt for scene understanding
3. call `infer_with_image(...)`
4. return a structured scene description

This pattern is useful for:

- robot environment summarization
- status reporting from a camera
- text-driven visual inspection tools

## Text-to-Image Note

The merged source explicitly noted that Ollama itself does not provide text-to-image generation. For local image generation, the lesson switched to a separate tool path such as FastSD CPU.

That means the offline multimodal chapter separates two ideas:

- vision-language models for understanding images
- separate local image-generation tools for creating images

## Video Analysis

The source material treated video analysis as repeated or structured image understanding over a sequence. In practice, this usually means:

- sample frames from a stream
- send those frames to a VLM
- ask for summary, event detection, or anomaly detection

## Visual Positioning

The merged source used multimodal models for tasks where the answer needs to include object location or spatial reasoning. Good prompts ask the model to:

- identify an object
- describe where it is
- optionally return coordinates or bounding-box-like structure

## Table Scan

One of the most concrete source applications was table extraction. The workflow was:

1. send an image containing a table to the VLM
2. ask for the result in Markdown
3. save the returned text as a `.md` file

This is a practical way to turn an image of a table into structured text.

## Autonomous Agent Pattern

The source lesson also merged an agent-style workflow where a large model:

- plans a multi-step task
- chooses tools
- uses tool outputs from previous steps
- keeps iterating until the task is complete

The important architectural idea is that image understanding becomes one callable tool inside a larger planning loop.

## Practical Advice

- Start with `qwen2.5vl` or `gemma3` if you want a lighter-entry multimodal setup.
- Use `llava` or `minicpm-v` when you need stronger image understanding and can afford more resources.
- Be explicit in prompts when you want structure such as Markdown tables or coordinate-like output.
- Keep the model configuration centralized so you can switch the back end without changing the rest of the application.
