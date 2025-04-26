import os
import sys
import json

# Use absolute import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add a type annotation comment to silence Pylance warnings
from path_manager import PathManager  # type: ignore

def load_config(config_path):
    # Resolve the absolute path to config.json
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), config_path))
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    # Add default values for missing keys
    default_config = {
        "headers": {},  # Default to an empty dictionary
        "custom_user_agent": None,
        "proxies": None,
        "rate_limit": 1,
        "timeout": 10,
        "retries": 3,
        "output_log_file": "output.log",  # Set a default log file
        "output_json_file": "output.json",
        "output_html_file": "output.html",
        "resume_file": "resume.txt",
        "status_codes_to_log": [200],
        "extensions": [""]
    }
    for key, value in default_config.items():
        config.setdefault(key, value)
    
    # Initialize PathManager
    path_manager = PathManager(base_directory=os.path.dirname(config_path))

    # Resolve and ensure directories and files for output
    for key in ["output_log_file", "output_json_file", "output_html_file", "resume_file"]:
        if config.get(key):
            resolved_path = path_manager.resolve_path(config[key])
            path_manager.ensure_file_exists(resolved_path)  # Ensure file exists
            config[key] = resolved_path  # Update to absolute path
    
    # Debugging: Print resolved paths
    for key in ["output_log_file", "output_json_file", "output_html_file", "resume_file"]:
        print(f"[DEBUG] Resolved path for {key}: {config[key]}")
    
    return config