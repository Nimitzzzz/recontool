"""
Port scanning using nmap
"""

import subprocess
import json
from pathlib import Path
from urllib.parse import urlparse


def scan_ports(live_hosts, output_dir, silent=False):
    """
    Scan top ports on live hosts using nmap
    Returns dictionary of host: ports
    """
    if not live_hosts:
        return {}
    
    output_file = Path(output_dir) / "ports.json"
    port_results = {}
    
    # Extract unique hosts
    hosts = set()
    for host_data in live_hosts:
        parsed = urlparse(host_data['url'])
        hostname = parsed.hostname or parsed.netloc
        if hostname:
            hosts.add(hostname)
    
    if not hosts:
        return {}
    
    if not silent:
        print(f"    Scanning {len(hosts)} unique hosts...")
    
    for host in hosts:
        try:
            if not silent:
                print(f"    Scanning: {host}")
            
            # Run nmap on top 100 ports
            cmd = [
                'nmap',
                '-Pn',  # Skip ping
                '--top-ports', '100',
                '-T4',  # Aggressive timing
                '--open',  # Only show open ports
                '-oX', '-',  # XML output to stdout
                host
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes per host
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse nmap XML output (basic parsing)
                open_ports = parse_nmap_xml(result.stdout)
                if open_ports:
                    port_results[host] = open_ports
                    if not silent:
                        print(f"      Found {len(open_ports)} open ports")
            
        except subprocess.TimeoutExpired:
            if not silent:
                print(f"      Timeout scanning {host}")
            continue
        except Exception as e:
            if not silent:
                print(f"      Error scanning {host}: {str(e)}")
            continue
    
    # Save results
    if port_results:
        with open(output_file, 'w') as f:
            json.dump(port_results, f, indent=2)
    
    return port_results


def parse_nmap_xml(xml_output):
    """
    Basic XML parsing for nmap output
    Returns list of open ports with service info
    """
    import re
    
    ports = []
    
    # Simple regex parsing (for production, use proper XML parser)
    port_pattern = r'<port protocol="([^"]+)" portid="([^"]+)">.*?<state state="open".*?(?:<service name="([^"]*)")?'
    matches = re.finditer(port_pattern, xml_output, re.DOTALL)
    
    for match in matches:
        protocol = match.group(1)
        port_id = match.group(2)
        service = match.group(3) if match.group(3) else 'unknown'
        
        ports.append({
            'port': int(port_id),
            'protocol': protocol,
            'service': service
        })
    
    return ports