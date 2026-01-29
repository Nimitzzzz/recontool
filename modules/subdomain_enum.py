"""
Subdomain enumeration using subfinder
"""

import subprocess
from pathlib import Path


def enumerate_subdomains(domain, output_dir, silent=False):
    """
    Enumerate subdomains using subfinder
    Returns list of discovered subdomains
    """
    output_file = Path(output_dir) / f"{domain}_subdomains.txt"
    subdomains = []
    
    try:
        # Run subfinder
        cmd = [
            'subfinder',
            '-d', domain,
            '-silent',
            '-o', str(output_file)
        ]
        
        if not silent:
            print(f"    Running: subfinder -d {domain}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode != 0:
            if not silent:
                print(f"[!] Subfinder error: {result.stderr}")
            return []
        
        # Read results
        if output_file.exists():
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
        
        # Also add the main domain
        if domain not in subdomains:
            subdomains.insert(0, domain)
            # Update file
            with open(output_file, 'w') as f:
                for sub in subdomains:
                    f.write(f"{sub}\n")
        
        return subdomains
        
    except subprocess.TimeoutExpired:
        if not silent:
            print(f"[!] Subfinder timeout for {domain}")
        return []
    except FileNotFoundError:
        print("[!] Subfinder not found. Install with: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
        return []
    except Exception as e:
        if not silent:
            print(f"[!] Error in subdomain enumeration: {str(e)}")
        return []