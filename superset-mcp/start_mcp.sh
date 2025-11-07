#!/bin/bash
# Start script for Superset MCP server with virtual environment
# Auto-setup virtual environment and dependencies if needed

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if virtual environment exists, create if not
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "🔧 Virtual environment not found. Creating..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    echo "✅ Virtual environment created at $SCRIPT_DIR/.venv"
fi

# Activate the virtual environment
echo "🔌 Activating virtual environment..."
source "$SCRIPT_DIR/.venv/bin/activate"

# Check if required packages are installed
echo "🔍 Checking dependencies..."
if ! python -c "import mcp, fastapi, httpx, uvicorn" 2>/dev/null; then
    echo "📦 Installing required dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install the package in editable mode (includes all dependencies)
    pip install -e "$SCRIPT_DIR"
    
    echo "✅ Dependencies installed successfully"
else
    echo "✅ All dependencies are already installed"
fi

# Verify installation
echo "🧪 Verifying installation..."
if ! python -c "import mcp.server.fastmcp" 2>/dev/null; then
    echo "❌ MCP installation verification failed"
    echo "📦 Attempting to reinstall dependencies..."
    pip install -e "$SCRIPT_DIR" --force-reinstall
fi

# Run the MCP server
echo "🚀 Starting Superset MCP server..."
python "$SCRIPT_DIR/main.py"
