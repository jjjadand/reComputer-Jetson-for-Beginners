# Offline Multimodal Voice Applications

This subchapter merges the highest-level assistant workflows from `xiaobai-lesson` Chapter 12, where speech, vision, and local reasoning are combined into one system.

## What Changes at This Stage

Modules 5.1 to 5.4 build the pieces. This chapter combines them into workflows such as:

- ask a voice question about a camera view
- inspect a scene and answer verbally
- analyze a table image and save the result
- run a multimodal agent that chains tools together
- boot an offline voice assistant automatically at startup

## Visual Understanding with Voice

The source lesson combined:

- a camera frame capture step
- a multimodal model like `qwen2.5vl`
- speech input
- spoken output

That creates a loop where a user can ask something like:

```text
What do you see?
```

and receive an answer generated from the current camera image.

## Image Generation and Video Analysis

The original source grouped image-generation and video-analysis demos alongside voice because the assistant can dispatch those capabilities as tools. In practice:

- image generation usually uses a dedicated local image model, not Ollama alone
- video analysis often reuses the same VLM layer frame by frame

Voice becomes the control interface rather than the core reasoning engine.

## Visual Positioning and Table Scan

Two especially practical applications from the source chapter were:

- visual positioning: ask where an object is and have the model describe or return its location
- table scanning: ask for a table to be extracted into Markdown and save the result as a file

These are strong examples of how multimodal models can produce structured outputs rather than only chat-style text.

## Autonomous Agent Workflow

The merged source spent significant time on an agent-style design:

- plan a task
- break it into steps
- call tools
- feed previous outputs into later steps
- summarize the result

This is useful when a single prompt is not enough and the system must:

- observe
- reason
- act
- observe again

## Offline Voice Assistant as a Service

The source chapter closed with an important deployment pattern: start the multimodal assistant automatically through `systemd`.

The high-level flow is:

1. configure offline ASR and offline TTS in YAML
2. ensure the model back end is set to `ollama`
3. rebuild the workspace
4. create a small startup script that sources ROS2 and the project workspace
5. create a `systemd` service to run the launch file at boot

This turns the tutorial stack into a persistent assistant service instead of a manual demo.

## Practical Advice

- Validate every component manually before converting it into a boot service.
- Keep ASR, TTS, and model platform settings in config rather than inside launch logic.
- Smaller Jetson models may not handle the full offline multimodal stack comfortably.
- Treat voice as the user interface layer and keep the underlying tool chain modular.
