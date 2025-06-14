#!/bin/sh
# Install Pipenv
pip install --user pipenv
export PATH="$HOME/.local/bin:$PATH"

# Create virtual environment and install dependencies
pipenv install