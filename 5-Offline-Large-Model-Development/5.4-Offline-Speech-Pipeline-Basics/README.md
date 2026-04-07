# Offline Speech Pipeline Basics

This subchapter merges the offline ASR, TTS, and speech-dialog loop content from `xiaobai-lesson` Chapter 12.

## Pipeline Overview

The source chapter broke the speech stack into four pieces:

1. microphone and speaker hardware connection
2. offline ASR
3. offline TTS
4. a local LLM loop that sits between them

That architecture is still the right mental model on Jetson.

## Hardware Connection

The source index listed a hardware-connection lesson before any ASR or TTS logic. The takeaway is simple:

- verify the microphone is visible to the system
- verify the speaker output works before debugging the language stack
- keep device naming stable if the project will run as a service

## Offline ASR

The merged source emphasized running offline ASR instead of online cloud transcription when privacy or network independence matters.

Typical configuration concerns:

- sample rate
- VAD sensitivity
- language selection
- microphone device index or serial port

In the Seeed-style configuration used by the source, this is handled through YAML config rather than hard-coded values.

## Offline TTS

Offline TTS takes model responses and turns them into speaker output without sending text to a remote service.

When debugging TTS:

- confirm the text is produced first
- confirm the TTS node receives it
- confirm the audio device and permissions are correct

## Connect Speech to the LLM Loop

The core offline interaction loop is:

1. record voice
2. convert voice to text
3. send text to the local model
4. convert the answer back to speech

That means you can validate the system in stages:

- text-only model works
- ASR works
- TTS works
- full loop works

## Practical Advice

- Debug ASR and TTS separately before you attempt a full assistant workflow.
- Keep everything offline first; only add online fallbacks if you really need them.
- Store language, device index, and runtime flags in config files so the same project can move between Jetson devices more easily.
