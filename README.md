# Ollama Model Collection

## Purpose

This repository maintains point-in-time snapshots of my local Ollama AI models and corresponding hardware specifications. The primary goals are:

- **Reproducibility**: Enable recreation of model environments on different systems
- **Change Tracking**: Monitor model usage patterns and collection evolution over time
- **Documentation**: Maintain detailed records of hardware configurations for performance reference
- **Backup Planning**: Keep inventory for disaster recovery and system migration

## Repository Structure

```
├── models-YYYY-MM-DD.md          # Timestamped model inventories
├── hardware-specs/               # Hardware specification snapshots
│   └── hardware-YYYY-MM-DD.md   # System specs for each snapshot date
└── README.md                     # This file
```

## Model Snapshots

Each model snapshot includes:
- Complete model inventory with sizes and IDs
- Inferred purpose for each model
- Performance notes and usage patterns
- Storage requirements and quantization details

## Hardware Specifications

Hardware snapshots document:
- CPU and GPU specifications
- Memory configuration
- ROCm version and GPU driver details
- Storage and network setup
- Performance context for AI workloads

## Usage

1. **Creating Snapshots**: Run `ollama ls` and system info commands on snapshot dates
2. **System Migration**: Use hardware specs to match or exceed capabilities on new systems
3. **Model Selection**: Reference usage patterns to prioritize which models to install
4. **Performance Baseline**: Compare inference speeds across different hardware configurations

## Current Status

- **Latest Snapshot**: August 25th, 2025
- **Model Count**: 12 models (~62.5 GB total)
- **Primary Model**: Llama 3.1 8B Instruct (daily driver)
- **Hardware**: Intel i7-12700F + AMD RX 7700 XT + 64GB RAM

---
*Maintained by Daniel Rosehill - [danielrosehill.com](https://danielrosehill.com)*
