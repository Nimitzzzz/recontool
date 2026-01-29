"""
Report generation module
"""

import json
import csv
from pathlib import Path
from datetime import datetime


def generate_report(results, output_dir, format_type, timestamp):
    """
    Generate final report in specified format(s)
    Returns list of generated file paths
    """
    output_files = []
    
    if format_type == 'all':
        formats = ['txt', 'json', 'csv']
    else:
        formats = [format_type]
    
    for fmt in formats:
        if fmt == 'txt':
            output_files.append(generate_txt_report(results, output_dir, timestamp))
        elif fmt == 'json':
            output_files.append(generate_json_report(results, output_dir, timestamp))
        elif fmt == 'csv':
            output_files.append(generate_csv_report(results, output_dir, timestamp))
    
    return output_files


def generate_txt_report(results, output_dir, timestamp):
    """
    Generate human-readable text report
    """
    report_file = Path(output_dir) / f"report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("RECONX RECONNAISSANCE REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Targets: {', '.join(results['targets'])}\n")
        f.write("=" * 80 + "\n\n")
        
        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        
        total_subdomains = sum(len(subs) for subs in results['subdomains'].values())
        total_live = sum(len(hosts) for hosts in results['live_hosts'].values())
        
        f.write(f"Total Subdomains Discovered: {total_subdomains}\n")
        f.write(f"Total Live Hosts: {total_live}\n")
        
        if results['ports']:
            total_hosts_scanned = sum(len(ports) for ports in results['ports'].values())
            f.write(f"Hosts with Open Ports: {total_hosts_scanned}\n")
        
        if results['headers']:
            total_checked = sum(len(headers) for headers in results['headers'].values())
            f.write(f"Hosts Checked for Security Headers: {total_checked}\n")
        
        f.write("\n" + "=" * 80 + "\n\n")
        
        # Detailed results per target
        for target in results['targets']:
            f.write(f"\nTARGET: {target}\n")
            f.write("=" * 80 + "\n\n")
            
            # Subdomains
            if target in results['subdomains']:
                subdomains = results['subdomains'][target]
                f.write(f"[+] Subdomains ({len(subdomains)})\n")
                f.write("-" * 80 + "\n")
                for sub in subdomains[:20]:  # Show first 20
                    f.write(f"  - {sub}\n")
                if len(subdomains) > 20:
                    f.write(f"  ... and {len(subdomains) - 20} more\n")
                f.write("\n")
            
            # Live hosts
            if target in results['live_hosts']:
                live_hosts = results['live_hosts'][target]
                f.write(f"[+] Live Hosts ({len(live_hosts)})\n")
                f.write("-" * 80 + "\n")
                for host in live_hosts:
                    f.write(f"  - {host['url']} [{host['status_code']}]")
                    if host.get('title'):
                        f.write(f" - {host['title'][:50]}")
                    f.write("\n")
                f.write("\n")
            
            # Port scan results
            if target in results['ports'] and results['ports'][target]:
                f.write(f"[+] Port Scan Results\n")
                f.write("-" * 80 + "\n")
                for host, ports in results['ports'][target].items():
                    f.write(f"  {host}:\n")
                    for port in ports:
                        f.write(f"    - {port['port']}/{port['protocol']} ({port['service']})\n")
                f.write("\n")
            
            # Security headers
            if target in results['headers'] and results['headers'][target]:
                f.write(f"[+] Security Headers Analysis\n")
                f.write("-" * 80 + "\n")
                for url, data in results['headers'][target].items():
                    if 'error' not in data:
                        f.write(f"  {url}\n")
                        f.write(f"    Score: {data['security_score']}/7\n")
                        if data['headers_missing']:
                            f.write(f"    Missing: {', '.join(data['headers_missing'])}\n")
                f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n\n")
    
    return str(report_file)


def generate_json_report(results, output_dir, timestamp):
    """
    Generate JSON report
    """
    report_file = Path(output_dir) / f"report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return str(report_file)


def generate_csv_report(results, output_dir, timestamp):
    """
    Generate CSV report for live hosts
    """
    report_file = Path(output_dir) / f"live_hosts_{timestamp}.csv"
    
    with open(report_file, 'w', newline='') as f:
        fieldnames = ['target', 'url', 'status_code', 'title', 'technologies']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for target in results['targets']:
            if target in results['live_hosts']:
                for host in results['live_hosts'][target]:
                    writer.writerow({
                        'target': target,
                        'url': host['url'],
                        'status_code': host['status_code'],
                        'title': host.get('title', ''),
                        'technologies': ', '.join(host.get('tech', []))
                    })
    
    return str(report_file)