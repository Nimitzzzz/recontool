"""
HTTP probing using httpx
"""

import subprocess
import json
from pathlib import Path


def probe_http(subdomains, output_dir, threads=50, silent=False):
    """
    Probe live HTTP/HTTPS hosts using httpx
    Returns list of live URLs with metadata
    """
    if not subdomains:
        return []
    
    # Create temp file for subdomains
    temp_input = Path(output_dir) / "temp_subdomains.txt"
    output_file = Path(output_dir) / "live_hosts.json"
    
    try:
        # Write subdomains to temp file
        with open(temp_input, 'w') as f:
            for sub in subdomains:
                f.write(f"{sub}\n")
        
        if not silent:
            print(f"    Running: httpx on {len(subdomains)} subdomains")
        
        # Run httpx
        cmd = [
            'httpx',
            '-l', str(temp_input),
            '-silent',
            '-json',
            '-status-code',
            '-title',
            '-tech-detect',
            '-threads', str(threads),
            '-timeout', '10',
            '-retries', '2'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        live_hosts = []
        
        if result.stdout:
            # Parse JSON lines
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        live_hosts.append({
                            'url': data.get('url', ''),
                            'status_code': data.get('status_code', 0),
                            'title': data.get('title', ''),
                            'tech': data.get('tech', []),
                            'content_length': data.get('content_length', 0),
                            'host': data.get('host', '')
                        })
                    except json.JSONDecodeError:
                        continue
        
        # Save results
        if live_hosts:
            with open(output_file, 'w') as f:
                json.dump(live_hosts, f, indent=2)
            
            # Also save simple list
            simple_list = Path(output_dir) / "live_hosts.txt"
            with open(simple_list, 'w') as f:
                for host in live_hosts:
                    f.write(f"{host['url']}\n")
        
        # Cleanup temp file
        temp_input.unlink(missing_ok=True)
        
        return live_hosts
        
    except subprocess.TimeoutExpired:
        if not silent:
            print(f"[!] HTTPx timeout")
        temp_input.unlink(missing_ok=True)
        return []
    except FileNotFoundError:
        print("[!] HTTPx not found. Install with: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest")
        return []
    except Exception as e:
        if not silent:
            print(f"[!] Error in HTTP probing: {str(e)}")
        temp_input.unlink(missing_ok=True)
        return []