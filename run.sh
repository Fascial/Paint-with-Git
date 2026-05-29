#!/bin/bash
cd "$(dirname "$0")"

if [ ! -f ".venv/bin/python" ]; then
    if ! command -v uv &> /dev/null; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    echo "Setting up environment for the first time..."
    uv sync
fi

.venv/bin/python -m src.ui &
disown