#!/usr/bin/env python3
"""
Concordia environment management script.
This script helps create and manage an isolated environment for Concordia and its dependencies.
"""
import subprocess
import sys
import os
from pathlib import Path
import argparse

def run_command(cmd, check=True):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(cmd, check=check, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        sys.exit(1)

def create_environment(args):
    """Create a new virtual environment for Concordia."""
    env_path = Path("concordia_env")
    if env_path.exists() and not args.recreate:
        print("Environment already exists. Use --recreate to create a new one.")
        return
    elif env_path.exists():
        print("Removing existing environment...")
        if sys.platform == "win32":
            run_command("rmdir /s /q concordia_env")
        else:
            run_command("rm -rf concordia_env")

    print("Creating Concordia virtual environment...")
    run_command("python -m venv concordia_env")
    
    # Install dependencies
    if sys.platform == "win32":
        pip_path = "concordia_env\\Scripts\\pip"
    else:
        pip_path = "concordia_env/bin/pip"
    
    print("Installing dependencies...")
    run_command(f"{pip_path} install -U pip")
    run_command(f"{pip_path} install -r concordia-requirements.txt")
    
    print("Environment created successfully!")

def activate_instructions():
    """Print instructions for activating the environment."""
    if sys.platform == "win32":
        print("\nTo activate the environment, run:")
        print("concordia_env\\Scripts\\activate")
    else:
        print("\nTo activate the environment, run:")
        print("source concordia_env/bin/activate")

def main():
    parser = argparse.ArgumentParser(description="Manage Concordia environment")
    parser.add_argument("--recreate", action="store_true", 
                      help="Recreate the environment if it exists")
    args = parser.parse_args()

    if not Path("concordia-requirements.txt").exists():
        print("Error: concordia-requirements.txt not found!")
        sys.exit(1)

    create_environment(args)
    activate_instructions()

if __name__ == "__main__":
    main()
