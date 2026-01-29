"""
Utility functions for ReconX
"""

import os
import shutil
from pathlib import Path


def check_dependencies():
    """
    Check if required CLI tools are installed
    Returns list of missing dependencies
    """
    required_tools = ['subfinder', 'httpx', 'nmap']
    missing = []
    
    for tool in required_tools:
        if not shutil.which(tool):
            missing.append(tool)
    
    return missing


def setup_output_dir(output_path):
    """
    Create output directory if it doesn't exist
    Returns Path object
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_targets(file_path):
    """
    Load targets from file (one per line)
    Returns list of domains
    """
    try:
        with open(file_path, 'r') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return targets
    except FileNotFoundError:
        print(f"[!] Error: File {file_path} not found")
        return []
    except Exception as e:
        print(f"[!] Error reading file: {str(e)}")
        return []


def save_list_to_file(data_list, file_path):
    """
    Save list of items to file (one per line)
    """
    try:
        with open(file_path, 'w') as f:
            for item in data_list:
                f.write(f"{item}\n")
        return True
    except Exception as e:
        print(f"[!] Error saving to {file_path}: {str(e)}")
        return False


def validate_domain(domain):
    """
    Basic domain validation
    """
    import re
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return re.match(pattern, domain) is not None