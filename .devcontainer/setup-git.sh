#!/bin/bash
# setup-git.sh


# Create the virtual environment
python3 -m venv /home/vscode/.local/os-venv


# Add venv activation to .bashrc for automatic activation in new terminals
echo 'source /home/vscode/.local/os-venv/bin/activate' >> ~/.bashrc


git config --global user.name "Erick Cantu Paz"
git config --global user.email "cantupaz@yahoo.com"

# Then clone and setup your repositories
# git clone https://${GITHUB_TOKEN}:x-oauth-basic@github.com/cantupaz/Modelo720.git /workspaces/Modelo720
# cd /workspaces/Modelo720
# /home/vscode/.local/os-venv/bin/pip install -r requirements.txt -e .

