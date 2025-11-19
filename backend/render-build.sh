#!/usr/bin/env bash
# Render build script to install system dependencies

# Install git (required by gitingest)
apt-get update
apt-get install -y git

# Install Python dependencies
pip install -r requirements.txt

