#!/usr/bin/env python3
"""
ReconX - Advanced Reconnaissance & Asset Discovery Tool
Author: Security Engineering Team
Purpose: Authorized penetration testing and bug bounty reconnaissance
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from modules.banner import print_banner
from modules.subdomain_enum import enumerate_subdomains
from modules.http_probe import probe_http
from modules.port_scan import scan_ports
from modules.header_check import check_security_headers
from modules.report import generate_report
from modules.utils import setup_output_dir, load_targets, check_dependencies


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='ReconX - Automated Reconnaissance & Asset Discovery',
        epilog='Example: reconx -d example.com --ports --headers'
    )
    
    # Target options
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        '-d', '--domain',
        help='Single target domain (e.g., example.com)'
    )
    target_group.add_argument(
        '-l', '--list',
        help='File containing list of domains (one per line)'
    )
    
    # Scan options
    parser.add_argument(
        '--ports',
        action='store_true',
        help='Enable port scanning (top 100 ports)'
    )
    parser.add_argument(
        '--headers',
        action='store_true',
        help='Check HTTP security headers'
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=50,
        help='Number of threads for HTTP probing (default: 50)'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        choices=['txt', 'json', 'csv', 'all'],
        default='txt',
        help='Output format (default: txt)'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory (default: ./output)'
    )
    
    # Behavior options
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Minimal output, only results'
    )
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Disable ASCII banner'
    )
    
    return parser.parse_args()


def main():
    """Main execution flow"""
    args = parse_arguments()
    
    # Display banner
    if not args.no_banner and not args.silent:
        print_banner()
    
    # Check dependencies
    if not args.silent:
        print("[*] Checking dependencies...")
    
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"[!] Missing dependencies: {', '.join(missing_deps)}")
        print("[*] Install with: apt-get install subfinder httpx-toolkit nmap")
        sys.exit(1)
    
    if not args.silent:
        print("[✓] All dependencies found\n")
    
    # Setup output directory
    output_dir = setup_output_dir(args.output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Load targets
    if args.domain:
        targets = [args.domain]
    else:
        targets = load_targets(args.list)
        if not targets:
            print(f"[!] No valid targets found in {args.list}")
            sys.exit(1)
    
    print(f"[*] Loaded {len(targets)} target(s)")
    print(f"[*] Output directory: {output_dir}\n")
    
    # Results storage
    all_results = {
        'targets': targets,
        'subdomains': {},
        'live_hosts': {},
        'ports': {},
        'headers': {},
        'timestamp': timestamp
    }
    
    # Process each target
    for target in targets:
        print(f"\n{'='*60}")
        print(f"[*] Processing target: {target}")
        print(f"{'='*60}\n")
        
        # Step 1: Subdomain Enumeration
        if not args.silent:
            print(f"[1/4] Enumerating subdomains for {target}...")
        
        subdomains = enumerate_subdomains(target, output_dir, args.silent)
        all_results['subdomains'][target] = subdomains
        
        if not args.silent:
            print(f"[✓] Found {len(subdomains)} subdomains\n")
        
        if not subdomains:
            print(f"[!] No subdomains found for {target}, skipping...\n")
            continue
        
        # Step 2: HTTP Probing
        if not args.silent:
            print(f"[2/4] Probing live hosts...")
        
        live_hosts = probe_http(subdomains, output_dir, args.threads, args.silent)
        all_results['live_hosts'][target] = live_hosts
        
        if not args.silent:
            print(f"[✓] Found {len(live_hosts)} live hosts\n")
        
        if not live_hosts:
            print(f"[!] No live hosts found for {target}, skipping...\n")
            continue
        
        # Step 3: Port Scanning (optional)
        if args.ports:
            if not args.silent:
                print(f"[3/4] Scanning ports on live hosts...")
            
            port_results = scan_ports(live_hosts, output_dir, args.silent)
            all_results['ports'][target] = port_results
            
            if not args.silent:
                print(f"[✓] Port scan completed\n")
        else:
            if not args.silent:
                print(f"[3/4] Port scanning disabled (use --ports to enable)\n")
        
        # Step 4: Security Headers Check (optional)
        if args.headers:
            if not args.silent:
                print(f"[4/4] Checking security headers...")
            
            header_results = check_security_headers(live_hosts, output_dir, args.silent)
            all_results['headers'][target] = header_results
            
            if not args.silent:
                print(f"[✓] Security headers check completed\n")
        else:
            if not args.silent:
                print(f"[4/4] Security headers check disabled (use --headers to enable)\n")
    
    # Generate final report
    print(f"\n{'='*60}")
    print("[*] Generating final report...")
    print(f"{'='*60}\n")
    
    report_files = generate_report(all_results, output_dir, args.output, timestamp)
    
    print("[✓] Reconnaissance completed!")
    print(f"\n[*] Results saved to:")
    for report_file in report_files:
        print(f"    - {report_file}")
    
    print(f"\n[*] Total execution time: {datetime.now()}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Fatal error: {str(e)}")
        sys.exit(1)