# Concordia Environment Management

This directory contains tools for managing an isolated environment for DeepMind's Concordia library and its dependencies. This setup helps prevent dependency conflicts with your main Python environment.

## Files

- `concordia-requirements.txt`: Contains all required and optional dependencies
- `manage_concordia.py`: Script to create and manage the isolated environment
- `concordia_env/`: Virtual environment directory (created when you run the management script)

## Setup Instructions

1. Create the isolated environment:
   ```bash
   ./manage_concordia.py
   ```

2. Activate the environment:
   - On Unix/macOS:
     ```bash
     source concordia_env/bin/activate
     ```
   - On Windows:
     ```bash
     concordia_env\Scripts\activate
     ```

3. To recreate the environment (if needed):
   ```bash
   ./manage_concordia.py --recreate
   ```

## Dependencies Overview

The environment includes:

### Core Dependencies
- Concordia and its direct requirements
- LLM frameworks (transformers, langchain)
- Google AI and Cloud services
- Data processing tools (pandas, numpy)

### Optional Dependencies
- Mistral AI integration
- Ollama for local models

To enable optional dependencies, uncomment them in `concordia-requirements.txt` before creating the environment.

## Usage

After activating the environment, you can use Concordia as normal:

```python
from concordia import Concordia
concord = Concordia()
```

## Deactivation

When you're done, deactivate the environment:
```bash
deactivate
```

## Troubleshooting

If you encounter dependency conflicts:

1. Try recreating the environment with `--recreate`
2. Check if any optional dependencies are causing conflicts
3. Make sure you're not mixing dependencies with your main environment

## Environment Maintenance

- Keep `concordia-requirements.txt` updated with your project's needs
- Consider pinning specific versions if you need stability
- Use `pip freeze > full-requirements.txt` inside the environment to capture exact versions
