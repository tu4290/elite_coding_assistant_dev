# Elite Coding Assistant

An advanced AI-powered coding assistant that orchestrates multiple specialized language models to provide expert-level programming assistance. The system implements a sophisticated multi-agent architecture with intelligent task routing and hierarchical fallback mechanisms.

## 🚀 Features

- **Multi-Model Orchestration**: Combines 5 specialized LLMs for optimal performance
- **Intelligent Task Routing**: Automatically selects the best model for each request
- **Hierarchical Fallback**: Ensures task completion even if primary models fail
- **Local Operation**: Runs entirely on your machine for privacy and control
- **Performance Monitoring**: Built-in metrics and health checking
- **Multiple Interfaces**: CLI, interactive mode, and batch processing

## 🏗️ Architecture

The Elite Coding Assistant operates as an autonomous AI development team:

### Team Structure

1. **Project Manager (Router)** - `openhermes:7b`
   - Task classification and delegation
   - Lightweight, fast response times
   - Intelligent routing decisions

2. **Quantitative Specialist** - `mathstral:7b`
   - Mathematical problem solving
   - Algorithm design and analysis
   - Statistical computations

3. **Lead Developer** - `deepseek-coder-v2:16b-lite-instruct`
   - Primary code generation
   - Multi-language programming
   - Code review and optimization

4. **Senior Developer** - `codellama:13b`
   - Quality assurance and fallback
   - Reliable, maintainable solutions
   - Cross-language expertise

5. **Principal Architect** - `wizardcoder:13b-python`
   - Complex system design
   - Advanced problem solving
   - Multi-step instruction following

### Request Flow

```
User Request → Project Manager → Task Classification
                    ↓
    ┌─────────────────────────────────────────┐
    ▼                                         ▼
Math Tasks                              General Tasks
    ▼                                         ▼
Quantitative Specialist              Lead Developer
    ▼                                         ▼
[Success] → Response                 [Success] → Response
    ▼                                         ▼
[Failure] → Principal Architect      [Failure] → Senior Developer
                                              ▼
                                     [Failure] → Principal Architect
```

## 📋 Requirements

### Hardware Requirements

**Minimum:**
- CPU: 8+ cores
- RAM: 32 GB
- Storage: 512 GB SSD
- GPU: Optional (NVIDIA with 8+ GB VRAM recommended)

**Recommended:**
- CPU: 12+ cores (Intel i9/AMD Ryzen 9)
- RAM: 64 GB
- Storage: 1 TB NVMe SSD
- GPU: NVIDIA RTX 4080/4090 (16-24 GB VRAM)

### Software Requirements

- Linux (Ubuntu 22.04+), macOS (12.0+), or Windows 11 with WSL2
- Python 3.8+
- Ollama
- 50+ GB free disk space

## 🛠️ Installation

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd elite_coding_assistant
   ```

2. **Run the setup script:**
   ```bash
   ./scripts/setup.sh
   ```

   This script will:
   - Install Ollama
   - Download all required models (~32 GB)
   - Set up Python environment
   - Install dependencies
   - Test the installation

### Manual Installation

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Download models:**
   ```bash
   ollama pull openhermes:7b
   ollama pull mathstral:7b
   ollama pull deepseek-coder-v2:16b-lite-instruct
   ollama pull codellama:13b
   ollama pull wizardcoder:13b-python
   ```

3. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Interactive Mode

Start an interactive chat session:

```bash
source venv/bin/activate
python src/cli.py --interactive
```

Example interaction:
```
You: Write a Python function to implement quicksort


Assistant: [Analyzing request...]
[Routing to Lead Developer...]

def quicksort(arr):
    """
    Implement quicksort algorithm with in-place partitioning.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Time Complexity: O(n log n) average, O(n²) worst case
# Space Complexity: O(log n) average due to recursion stack

[Response time: 2.3s]
```

### Command Line Options

```bash
# Interactive mode (default)
python src/cli.py --interactive

# Process batch file
python src/cli.py --batch requests.txt --output results.json

# System management
python src/cli.py --install          # Install missing models
python src/cli.py --report           # Generate system report
python src/cli.py --benchmark        # Benchmark all models

# Configuration management
python src/cli.py --config-export config.json
python src/cli.py --config-import config.json
```

### Batch Processing

Create a file with requests (one per line):

```text
Write a REST API endpoint for user authentication
Implement binary search algorithm
Calculate the derivative of x^3 + 2x^2 - 5
Design a database schema for an e-commerce system
```

Process the batch:
```bash
python src/cli.py --batch requests.txt --output results.json
```

### Python API

Use the assistant programmatically:

```python
from src.coding_director import CodingDirector

# Initialize the assistant
director = CodingDirector()

# Get coding assistance
response = director.get_assistance("Write a function to validate email addresses")
print(response)

# Check performance metrics
metrics = director.get_metrics_summary()
print(f"Success rate: {metrics['success_rate']:.1f}%")
print(f"Average response time: {metrics['average_response_time']:.2f}s")
```

## 📊 Performance Optimization

### Environment Variables

Configure performance settings:

```bash
# Memory management
export OLLAMA_MAX_LOADED_MODELS=5
export OLLAMA_KEEP_ALIVE=10m

# Parallel processing
export OLLAMA_NUM_PARALLEL=3
export OLLAMA_MAX_QUEUE=10

# GPU acceleration (if available)
export OLLAMA_GPU_LAYERS=35
export OLLAMA_GPU_MEMORY_FRACTION=0.8
```

### System Tuning

For optimal performance:

1. **Memory**: Ensure 64GB+ RAM for comfortable operation
2. **Storage**: Use NVMe SSD for model storage
3. **CPU**: Enable all cores with `OLLAMA_NUM_PARALLEL`
4. **GPU**: Configure GPU layers for acceleration

### Monitoring

Check system health:

```bash
python src/cli.py --report
```

Monitor real-time performance:
```bash
# System resources
htop
iotop
nvidia-smi -l 1  # For GPU monitoring

# Ollama logs
journalctl -u ollama -f
```

## 🔧 Configuration

### Model Configuration

Customize model behavior in `config/models.json`:

```json
{
  "lead_developer": {
    "name": "Lead Developer",
    "model_id": "deepseek-coder-v2:16b-lite-instruct",
    "performance": {
      "temperature": 0.2,
      "max_tokens": 3000,
      "top_p": 0.9
    },
    "system_prompt": "You are an expert developer..."
  }
}
```

### System Configuration

Adjust system settings in `config/system.json`:

```json
{
  "log_level": "INFO",
  "max_concurrent_requests": 3,
  "request_timeout": 300,
  "ollama_host": "localhost",
  "ollama_port": 11434
}
```

### User Preferences

Customize user settings in `config/user.json`:

```json
{
  "preferred_language": "python",
  "code_style": "pep8",
  "explanation_level": "detailed",
  "include_comments": true,
  "include_tests": false
}
```

## 🧪 Testing

Run the test suite:

```bash
# Basic functionality tests
python examples/usage_examples.py

# Model health check
python src/model_manager.py

# Configuration validation
python src/config_manager.py

# Full system test
python src/cli.py --benchmark
```

## 📈 Monitoring and Metrics

### Built-in Metrics

The system tracks:
- Request success/failure rates
- Response times per model
- Model usage patterns
- System resource utilization
- Error rates and types

### Health Monitoring

Regular health checks include:
- Model availability and functionality
- System resource usage
- Performance benchmarks
- Configuration validation

### Performance Reports

Generate comprehensive reports:

```bash
# System status
python src/cli.py --report

# Performance benchmarks
python src/cli.py --benchmark --output benchmark_results.json

# Export metrics
python -c "
from src.coding_director import CodingDirector
director = CodingDirector()
# ... use the assistant ...
metrics = director.get_metrics_summary()
print(json.dumps(metrics, indent=2))
"
```

## 🔍 Troubleshooting

### Common Issues

**Models not responding:**
```bash
# Check Ollama service
systemctl status ollama

# Restart if needed
sudo systemctl restart ollama

# Verify model installation
ollama list
```

**High memory usage:**
```bash
# Reduce concurrent models
export OLLAMA_MAX_LOADED_MODELS=3

# Shorter keep-alive time
export OLLAMA_KEEP_ALIVE=5m

# Monitor memory usage
free -h
```

**Slow response times:**
```bash
# Check system resources
htop
iotop

# Reduce parallel requests
export OLLAMA_NUM_PARALLEL=2

# Enable GPU acceleration
export OLLAMA_GPU_LAYERS=35
```

### Log Analysis

Check logs for issues:

```bash
# Application logs
tail -f elite_coding_assistant.log

# Ollama service logs
journalctl -u ollama -f

# System logs
dmesg | tail
```

### Recovery Procedures

**Reset configuration:**
```bash
# Backup current config
cp -r config config.backup

# Reset to defaults
rm -rf config
python src/config_manager.py
```

**Reinstall models:**
```bash
# Remove all models
ollama list | grep -v NAME | awk '{print $1}' | xargs -I {} ollama rm {}

# Reinstall
./scripts/setup.sh --force
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a development branch
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8 mypy
   ```

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for all functions and classes
- Write unit tests for new features

### Testing

Run tests before submitting:

```bash
# Code formatting
black src/
flake8 src/

# Type checking
mypy src/

# Unit tests
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for providing the local LLM runtime
- **OpenHermes** for the routing model
- **Mathstral** for mathematical reasoning
- **DeepSeek** for advanced code generation
- **CodeLlama** for reliable coding assistance
- **WizardCoder** for complex problem solving

## 📞 Support

For support and questions:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Run the health check: `python src/cli.py --report`
4. Create an issue with system information and logs

## 🗺️ Roadmap

### Planned Features

- [ ] Web interface for browser-based interaction
- [ ] IDE plugins (VS Code, PyCharm, etc.)
- [ ] Custom model fine-tuning support
- [ ] Distributed deployment across multiple machines
- [ ] Integration with external APIs and services
- [ ] Advanced code analysis and refactoring tools
- [ ] Team collaboration features
- [ ] Performance optimization recommendations

### Version History

- **v1.0** - Initial release with core functionality
- **v1.1** - Performance optimizations and bug fixes (planned)
- **v2.0** - Web interface and IDE integrations (planned)

---

**Elite Coding Assistant** - Empowering developers with AI-driven coding excellence.

