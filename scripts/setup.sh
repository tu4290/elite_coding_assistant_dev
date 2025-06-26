#!/bin/bash
# Elite Coding Assistant - Setup Script
# ====================================
# 
# This script sets up the Elite Coding Assistant system including
# Ollama installation, model downloads, and Python environment setup.
#
# Author: Manus AI
# Version: 1.0
# Date: June 23, 2025

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check available memory
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$MEMORY_GB" -lt 32 ]; then
        log_warning "System has ${MEMORY_GB}GB RAM. Recommended: 32GB or more"
        log_warning "Performance may be limited with insufficient memory"
    else
        log_success "Memory check passed: ${MEMORY_GB}GB RAM available"
    fi
    
    # Check available disk space
    DISK_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_GB" -lt 50 ]; then
        log_error "Insufficient disk space. Available: ${DISK_GB}GB, Required: 50GB+"
        exit 1
    else
        log_success "Disk space check passed: ${DISK_GB}GB available"
    fi
    
    # Check for required commands
    for cmd in curl python3 pip3; do
        if ! command -v $cmd &> /dev/null; then
            log_error "Required command not found: $cmd"
            exit 1
        fi
    done
    
    log_success "System requirements check completed"
}

# Install Ollama
install_ollama() {
    log_info "Installing Ollama..."
    
    if command -v ollama &> /dev/null; then
        log_info "Ollama already installed, checking version..."
        ollama --version
    else
        log_info "Downloading and installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Verify installation
        if command -v ollama &> /dev/null; then
            log_success "Ollama installed successfully"
        else
            log_error "Ollama installation failed"
            exit 1
        fi
    fi
    
    # Start Ollama service
    log_info "Starting Ollama service..."
    if systemctl is-active --quiet ollama; then
        log_info "Ollama service already running"
    else
        sudo systemctl start ollama
        sudo systemctl enable ollama
        log_success "Ollama service started and enabled"
    fi
    
    # Wait for service to be ready
    log_info "Waiting for Ollama service to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            log_success "Ollama service is ready"
            break
        fi
        sleep 2
        if [ $i -eq 30 ]; then
            log_error "Ollama service failed to start properly"
            exit 1
        fi
    done
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python environment..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_info "Python version: $PYTHON_VERSION"
    
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
        log_success "Python version check passed"
    else
        log_error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment and install dependencies
    log_info "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "Python environment setup completed"
}

# Download required models
download_models() {
    log_info "Downloading required models..."
    log_warning "This may take a while depending on your internet connection"
    
    # List of required models
    MODELS=(
        "openhermes:7b"
        "mathstral:7b"
        "deepseek-coder-v2:16b-lite-instruct"
        "codellama:13b"
        "wizardcoder:13b-python"
    )
    
    for model in "${MODELS[@]}"; do
        log_info "Downloading $model..."
        if ollama pull "$model"; then
            log_success "Downloaded $model"
        else
            log_error "Failed to download $model"
            exit 1
        fi
    done
    
    log_success "All models downloaded successfully"
}

# Test installation
test_installation() {
    log_info "Testing installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test model manager
    log_info "Testing model manager..."
    if python3 src/model_manager.py; then
        log_success "Model manager test passed"
    else
        log_error "Model manager test failed"
        exit 1
    fi
    
    # Test configuration manager
    log_info "Testing configuration manager..."
    if python3 src/config_manager.py; then
        log_success "Configuration manager test passed"
    else
        log_error "Configuration manager test failed"
        exit 1
    fi
    
    # Test coding director with a simple prompt
    log_info "Testing coding director..."
    if python3 -c "
from src.coding_director import CodingDirector
director = CodingDirector()
response = director.get_assistance('Write a simple hello world function in Python')
print('Test response length:', len(response))
assert len(response) > 10, 'Response too short'
print('Coding director test passed')
"; then
        log_success "Coding director test passed"
    else
        log_error "Coding director test failed"
        exit 1
    fi
    
    log_success "Installation test completed successfully"
}

# Create desktop shortcut (Linux only)
create_shortcuts() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Creating desktop shortcuts..."
        
        DESKTOP_DIR="$HOME/Desktop"
        if [ -d "$DESKTOP_DIR" ]; then
            cat > "$DESKTOP_DIR/Elite Coding Assistant.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Elite Coding Assistant
Comment=AI-powered coding assistance
Exec=$(pwd)/venv/bin/python $(pwd)/src/cli.py
Icon=applications-development
Terminal=true
Categories=Development;
EOF
            chmod +x "$DESKTOP_DIR/Elite Coding Assistant.desktop"
            log_success "Desktop shortcut created"
        fi
    fi
}

# Main setup function
main() {
    echo "Elite Coding Assistant - Setup Script"
    echo "====================================="
    echo
    
    check_root
    check_requirements
    install_ollama
    setup_python_env
    download_models
    test_installation
    create_shortcuts
    
    echo
    log_success "Setup completed successfully!"
    echo
    echo "To start the Elite Coding Assistant:"
    echo "  1. Activate the virtual environment: source venv/bin/activate"
    echo "  2. Run the CLI: python src/cli.py"
    echo
    echo "For interactive mode: python src/cli.py --interactive"
    echo "For help: python src/cli.py --help"
    echo
    echo "Enjoy your Elite Coding Assistant!"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Elite Coding Assistant Setup Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --skip-models  Skip model downloads (for testing)"
        echo "  --force        Force reinstallation of components"
        echo
        exit 0
        ;;
    --skip-models)
        SKIP_MODELS=true
        ;;
    --force)
        FORCE_INSTALL=true
        ;;
esac

# Run main setup
main

