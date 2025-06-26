# Elite Coding Assistant - Quick Start Guide

## Overview

The Elite Coding Assistant is a sophisticated AI-powered coding system that orchestrates 5 specialized language models to provide expert-level programming assistance. This quick start guide gets you up and running in under 30 minutes.

## Prerequisites

- **Hardware**: 8+ CPU cores, 32+ GB RAM, 50+ GB free storage
- **Software**: Linux/macOS/Windows with WSL2, Python 3.8+
- **Network**: Stable internet for initial model downloads (~32 GB)

## Quick Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd elite_coding_assistant

# Run the automated setup script
./scripts/setup.sh
```

The setup script will:
- Install Ollama
- Download all 5 required models
- Set up Python environment
- Install dependencies
- Test the installation

### Option 2: Manual Setup

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Download models (this takes time!)
ollama pull openhermes:7b
ollama pull mathstral:7b
ollama pull deepseek-coder-v2:16b-lite-instruct
ollama pull codellama:13b
ollama pull wizardcoder:13b-python

# 3. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## First Run

### Interactive Mode

```bash
# Activate the environment
source venv/bin/activate

# Start interactive mode
python src/cli.py --interactive
```

### Test the System

```
You: Write a Python function to calculate factorial


Assistant: [Analyzing request...]
[Routing to Lead Developer...]

def factorial(n):
    """Calculate factorial of a number."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

# Example usage
print(factorial(5))  # Output: 120

[Response time: 1.8s]
```

## System Architecture

Your Elite Coding Assistant consists of 5 specialized models:

1. **Project Manager** (`openhermes:7b`) - Routes requests
2. **Quantitative Specialist** (`mathstral:7b`) - Math & algorithms  
3. **Lead Developer** (`deepseek-coder-v2:16b`) - Primary coding
4. **Senior Developer** (`codellama:13b`) - Quality assurance
5. **Principal Architect** (`wizardcoder:13b-python`) - Complex design

## Common Commands

```bash
# Interactive chat
python src/cli.py --interactive

# Process batch file
python src/cli.py --batch requests.txt

# System health check
python src/cli.py --report

# Install missing models
python src/cli.py --install

# Benchmark performance
python src/cli.py --benchmark
```

## Example Requests

Try these examples to test different capabilities:

### Mathematical Tasks
- "Calculate the derivative of x^3 + 2x^2 - 5"
- "Implement quicksort and analyze its complexity"
- "Write a function to find prime numbers using Sieve of Eratosthenes"

### Web Development
- "Create a Flask REST API for user authentication"
- "Write responsive CSS for a mobile-first design"
- "Build a React component for a todo list"

### System Design
- "Design a microservices architecture for e-commerce"
- "Explain database indexing strategies"
- "Create a caching layer for high-traffic applications"

## Performance Tips

### Memory Optimization
```bash
# Reduce concurrent models if memory is limited
export OLLAMA_MAX_LOADED_MODELS=3

# Shorter keep-alive time
export OLLAMA_KEEP_ALIVE=5m
```

### GPU Acceleration (if available)
```bash
# Enable GPU layers
export OLLAMA_GPU_LAYERS=35

# Set GPU memory fraction
export OLLAMA_GPU_MEMORY_FRACTION=0.8
```

## Troubleshooting

### Models Not Loading
```bash
# Check Ollama service
systemctl status ollama

# Restart if needed
sudo systemctl restart ollama

# Verify models
ollama list
```

### Slow Performance
```bash
# Check system resources
htop
free -h

# Monitor GPU (if available)
nvidia-smi
```

### Memory Issues
```bash
# Check memory usage
free -h

# Reduce parallel requests
export OLLAMA_NUM_PARALLEL=2
```

## Getting Help

### Built-in Help
```bash
# CLI help
python src/cli.py --help

# Interactive mode commands
help     # Show available commands
status   # System status
metrics  # Performance metrics
```

### System Status
```bash
# Quick health check
python src/cli.py --report

# Detailed system information
python src/model_manager.py
```

## Next Steps

1. **Explore Examples**: Run `python examples/usage_examples.py`
2. **Read Full Guide**: See `elite_coding_assistant_guide.pdf`
3. **Customize Configuration**: Edit files in `config/` directory
4. **Integrate with IDE**: Set up VS Code or PyCharm integration

## Support

- Check the troubleshooting section in the full guide
- Review logs: `tail -f elite_coding_assistant.log`
- Run health check: `python src/cli.py --report`

---

**You're ready to go!** Start with `python src/cli.py --interactive` and begin coding with your AI team.

