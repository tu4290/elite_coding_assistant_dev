#!/bin/bash
# Enhanced Elite Coding Assistant - Complete Setup Script
# Version: 2.0
# Author: Manus AI
# Date: June 23, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
fi

log "Starting Enhanced Elite Coding Assistant Setup..."

# System requirements check
log "Checking system requirements..."

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    log "Detected Linux OS"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    log "Detected macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
    log "Detected Windows with WSL/Cygwin"
else
    error "Unsupported operating system: $OSTYPE"
fi

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [[ $PYTHON_MAJOR -eq 3 ]] && [[ $PYTHON_MINOR -ge 8 ]]; then
        log "Python $PYTHON_VERSION detected - OK"
    else
        error "Python 3.8+ required, found $PYTHON_VERSION"
    fi
else
    error "Python 3 not found. Please install Python 3.8 or later"
fi

# Check available disk space (need ~50GB)
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
REQUIRED_SPACE=52428800  # 50GB in KB

if [[ $AVAILABLE_SPACE -lt $REQUIRED_SPACE ]]; then
    warn "Low disk space detected. At least 50GB recommended for models and data"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check memory (recommend 32GB+)
TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
if [[ $TOTAL_MEM -lt 32 ]]; then
    warn "System has ${TOTAL_MEM}GB RAM. 32GB+ recommended for optimal performance"
fi

log "System requirements check completed"

# Create project directory
PROJECT_DIR="$HOME/enhanced_elite_coding_assistant"
if [[ -d "$PROJECT_DIR" ]]; then
    warn "Project directory already exists: $PROJECT_DIR"
    read -p "Remove existing directory and reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
        log "Removed existing directory"
    else
        error "Installation cancelled"
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
log "Created project directory: $PROJECT_DIR"

# Install Ollama
log "Installing Ollama..."
if command -v ollama &> /dev/null; then
    log "Ollama already installed"
else
    if [[ "$OS" == "linux" ]] || [[ "$OS" == "windows" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OS" == "macos" ]]; then
        # For macOS, user needs to download manually
        warn "Please download and install Ollama from https://ollama.ai/download"
        read -p "Press Enter after installing Ollama..."
    fi
    
    # Verify installation
    if command -v ollama &> /dev/null; then
        log "Ollama installed successfully"
    else
        error "Ollama installation failed"
    fi
fi

# Start Ollama service
log "Starting Ollama service..."
if [[ "$OS" == "linux" ]]; then
    sudo systemctl start ollama || true
    sudo systemctl enable ollama || true
elif [[ "$OS" == "macos" ]]; then
    # On macOS, Ollama runs as an app
    open -a Ollama || warn "Please start Ollama app manually"
fi

# Wait for Ollama to be ready
log "Waiting for Ollama to be ready..."
for i in {1..30}; do
    if ollama list &> /dev/null; then
        log "Ollama is ready"
        break
    fi
    if [[ $i -eq 30 ]]; then
        error "Ollama failed to start within 30 seconds"
    fi
    sleep 1
done

# Download models
log "Downloading language models (this will take a while - ~32GB total)..."

MODELS=(
    "openhermes:7b"
    "mathstral:7b"
    "deepseek-coder-v2:16b-lite-instruct"
    "codellama:13b"
    "wizardcoder:13b-python"
)

for model in "${MODELS[@]}"; do
    log "Downloading $model..."
    if ollama pull "$model"; then
        log "Successfully downloaded $model"
    else
        error "Failed to download $model"
    fi
done

log "All models downloaded successfully"

# Create Python virtual environment
log "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
log "Virtual environment created and activated"

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip

# Copy project files (assuming they're in the current directory)
log "Setting up project structure..."
mkdir -p {src,config,scripts,tests,docs,examples,knowledge,data}

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Enhanced Elite Coding Assistant - Python Dependencies
# Version: 2.0

# Core AI and ML frameworks
pydantic-ai>=0.0.13
pydantic>=2.5.0
ollama>=0.1.7

# Database and storage
supabase>=2.3.0
psycopg2-binary>=2.9.7
sqlalchemy>=2.0.23

# Web and API frameworks
fastapi>=0.104.1
uvicorn>=0.24.0
httpx>=0.25.2
aiohttp>=3.9.1

# Data processing and analysis
pandas>=2.1.3
numpy>=1.24.3
scikit-learn>=1.3.2
matplotlib>=3.8.2
seaborn>=0.13.0

# Natural language processing
transformers>=4.36.0
sentence-transformers>=2.2.2
nltk>=3.8.1
spacy>=3.7.2

# Document processing
pypdf2>=3.0.1
python-docx>=1.1.0
markdown>=3.5.1
beautifulsoup4>=4.12.2

# CLI and user interface
click>=8.1.7
rich>=13.7.0
prompt-toolkit>=3.0.41

# Utilities and helpers
python-dotenv>=1.0.0
pyyaml>=6.0.1
jsonschema>=4.20.0
python-dateutil>=2.8.2
requests>=2.31.0

# Development and testing
pytest>=7.4.3
pytest-asyncio>=0.21.1
black>=23.11.0
flake8>=6.1.0
mypy>=1.7.1

# Monitoring and logging
structlog>=23.2.0
prometheus-client>=0.19.0

# Security
cryptography>=41.0.8
python-jose>=3.3.0
passlib>=1.7.4

# Async and concurrency
asyncio-mqtt>=0.16.1
aiofiles>=23.2.1
EOF

# Install Python dependencies
log "Installing Python dependencies..."
pip install -r requirements.txt
log "Python dependencies installed successfully"

# Create configuration files
log "Creating configuration files..."

# Main configuration
cat > config/config.yaml << 'EOF'
# Enhanced Elite Coding Assistant Configuration
version: "2.0"

# Database configuration
database:
  provider: "supabase"
  url: "${SUPABASE_URL}"
  key: "${SUPABASE_ANON_KEY}"
  service_key: "${SUPABASE_SERVICE_KEY}"

# Model configuration
models:
  openhermes:
    name: "openhermes:7b"
    role: "router"
    timeout: 30
    temperature: 0.3
    max_tokens: 2048
  
  mathstral:
    name: "mathstral:7b"
    role: "quantitative_specialist"
    timeout: 45
    temperature: 0.2
    max_tokens: 4096
  
  deepseek:
    name: "deepseek-coder-v2:16b-lite-instruct"
    role: "lead_developer"
    timeout: 60
    temperature: 0.4
    max_tokens: 8192
  
  codellama:
    name: "codellama:13b"
    role: "senior_developer"
    timeout: 45
    temperature: 0.3
    max_tokens: 4096
  
  wizardcoder:
    name: "wizardcoder:13b-python"
    role: "principal_architect"
    timeout: 60
    temperature: 0.5
    max_tokens: 8192

# Learning configuration
learning:
  enabled: true
  adaptation_rate: 0.1
  confidence_threshold: 0.7
  feedback_weight: 0.8
  pattern_recognition: true
  auto_optimization: true

# Performance configuration
performance:
  max_concurrent_requests: 5
  cache_size: 1000
  response_timeout: 120
  retry_attempts: 3

# Security configuration
security:
  encryption_enabled: true
  audit_logging: true
  data_retention_days: 365
  privacy_mode: false

# Logging configuration
logging:
  level: "INFO"
  format: "structured"
  file_enabled: true
  console_enabled: true
EOF

# Create environment template
cat > .env.template << 'EOF'
# Enhanced Elite Coding Assistant Environment Variables
# Copy this file to .env and fill in your values

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# OpenAI API Key (optional, for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# System Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here
EOF

# Create startup script
cat > scripts/start.sh << 'EOF'
#!/bin/bash
# Enhanced Elite Coding Assistant Startup Script

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [[ ! -f .env ]]; then
    echo "Error: .env file not found. Please copy .env.template to .env and configure it."
    exit 1
fi

# Load environment variables
source .env

# Start the enhanced CLI
python src/enhanced_cli.py interactive
EOF

chmod +x scripts/start.sh

# Create test script
cat > scripts/test.sh << 'EOF'
#!/bin/bash
# Enhanced Elite Coding Assistant Test Script

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment
source venv/bin/activate

echo "Running system tests..."

# Test Ollama connectivity
echo "Testing Ollama connectivity..."
if ollama list &> /dev/null; then
    echo "✓ Ollama is accessible"
else
    echo "✗ Ollama is not accessible"
    exit 1
fi

# Test model availability
echo "Testing model availability..."
MODELS=("openhermes:7b" "mathstral:7b" "deepseek-coder-v2:16b-lite-instruct" "codellama:13b" "wizardcoder:13b-python")

for model in "${MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "✓ $model is available"
    else
        echo "✗ $model is not available"
        exit 1
    fi
done

# Test Python environment
echo "Testing Python environment..."
python -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import pydantic_ai
    print('✓ Pydantic AI imported successfully')
except ImportError as e:
    print(f'✗ Pydantic AI import failed: {e}')
    sys.exit(1)

try:
    import supabase
    print('✓ Supabase client imported successfully')
except ImportError as e:
    print(f'✗ Supabase import failed: {e}')
    sys.exit(1)

try:
    import ollama
    print('✓ Ollama client imported successfully')
except ImportError as e:
    print(f'✗ Ollama import failed: {e}')
    sys.exit(1)

print('✓ All core dependencies are available')
"

echo "All tests passed! Enhanced Elite Coding Assistant is ready to use."
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and configure your Supabase credentials"
echo "2. Run './scripts/start.sh' to start the interactive assistant"
echo "3. See the documentation for advanced configuration options"
EOF

chmod +x scripts/test.sh

# Create README
cat > README.md << 'EOF'
# Enhanced Elite Coding Assistant

A sophisticated AI-powered coding assistant that orchestrates multiple specialized language models with advanced learning capabilities.

## Quick Start

1. **Configure Environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your Supabase credentials
   ```

2. **Start the Assistant**:
   ```bash
   ./scripts/start.sh
   ```

3. **Run Tests**:
   ```bash
   ./scripts/test.sh
   ```

## Features

- **Multi-Model Orchestration**: 5 specialized AI models working together
- **Continuous Learning**: Improves from every interaction
- **Knowledge Management**: Learns from documentation and code repositories
- **Adaptive Routing**: Intelligent model selection based on request type
- **Comprehensive Analytics**: Detailed performance monitoring and insights

## Documentation

See the complete documentation in `docs/` for detailed setup, configuration, and usage instructions.

## Support

For issues and questions, please refer to the documentation or create an issue in the project repository.
EOF

log "Configuration files created successfully"

# Run initial tests
log "Running initial system tests..."
./scripts/test.sh

log "Setup completed successfully!"
echo ""
echo -e "${GREEN}🎉 Enhanced Elite Coding Assistant Setup Complete! 🎉${NC}"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and configure your Supabase credentials:"
echo "   cp .env.template .env"
echo "   # Edit .env with your database credentials"
echo ""
echo "2. Start the assistant:"
echo "   ./scripts/start.sh"
echo ""
echo "3. For detailed documentation, see:"
echo "   - README.md (quick start)"
echo "   - docs/ directory (comprehensive guides)"
echo ""
echo "The system is now ready to provide intelligent coding assistance!"
echo "Total installation size: ~32GB (models) + ~500MB (dependencies)"

