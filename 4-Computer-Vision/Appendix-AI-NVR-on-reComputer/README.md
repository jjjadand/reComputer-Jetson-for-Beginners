# Appendix: AI NVR on reComputer

## Why This Appendix Exists

The main 10-section course is designed around a clean learning spine:

- foundations
- methods
- tasks
- training
- deployment
- Jetson system concepts
- frontier outlook

An `AI NVR` project is extremely valuable, but it works best as an extension after the learner has already completed the main sequence. That is why it appears here as an appendix rather than as one of the main 10 sections.

## Project Goal

Build an `AI NVR` workflow on `reComputer` that combines:

- camera ingestion
- live inference
- tracking
- event logic
- recording and storage
- operator-facing visualization

## What This Project Brings Together

This appendix is useful because it combines ideas from multiple earlier chapters:

- `4.2`: image and video input
- `4.5`: vision tasks such as detection and tracking
- `4.6`: model usage and evaluation
- `4.7`: deployment formats and optimization
- `4.8`: pipeline thinking
- `4.9`: DeepStream and Jetson services

## Recommended Architecture

- `VST` for stream onboarding and video handling
- `DeepStream Perception` for inference
- `Analytics` for ROI, counting, or line-crossing logic
- `Redis` for metadata
- `Ingress` for service access

## Minimal Project Sequence

1. prepare the Jetson baseline
2. verify JPS services
3. add one or more camera streams
4. launch inference
5. confirm tracking or event logic
6. inspect recordings and storage behavior
7. validate the operator experience

## Example Service Startup

```bash
sudo systemctl start jetson-redis
sudo systemctl start jetson-ingress
sudo systemctl start jetson-vst
```

## Reflection Questions

1. Which parts of the project depend on model quality, and which depend on system design?
2. What would fail first in a real deployment: the model, the stream, the storage, or the operator workflow?
3. How would you extend this appendix into a production pilot?

## Summary

This appendix gives learners a concrete project that connects the course's theory and system practice. It is not the center of the curriculum, but it is a powerful extension for learners who want to see how a complete edge vision application comes together.

## References

- [AI NVR Setup Guide](https://docs.nvidia.com/jetson/jps/setup/ai-nvr.html)
- [Jetson Platform Services Quick Start](https://docs.nvidia.com/jetson/jps/setup/quick-start.html)
- [DeepStream Perception on JPS](https://docs.nvidia.com/jetson/jps/deepstream/deepstream.html)
