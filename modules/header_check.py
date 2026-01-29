"""
Security headers checker
"""

import requests
import json
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Security headers to check
SECURITY_HEADERS = {
    'Strict-Transport-Security': 'HSTS',
    'Content-Security-Policy': 'CSP',
    'X-Frame-Options': 'X-Frame-Options',
    'X-Content-Type-Options': 'X-Content-Type-Options',
    'X-XSS-Protection': 'X-XSS-Protection',
    'Referrer-Policy': 'Referrer-Policy',
    'Permissions-Policy': 'Permissions-Policy'
}


def check_security_headers(live_hosts, output_dir, silent=False):
    """
    Check security headers for each live host
    Returns dictionary of URL: header analysis
    """
    if not live_hosts:
        return {}
    
    output_file = Path(output_dir) / "security_headers.json"
    results = {}
    
    if not silent:
        print(f"    Checking {len(live_hosts)} hosts...")
    
    for host_data in live_hosts:
        url = host_data['url']
        
        try:
            if not silent:
                print(f"    Checking: {url}")
            
            # Make request
            response = requests.get(
                url,
                timeout=10,
                verify=False,  # Skip SSL verification for testing
                allow_redirects=True,
                headers={'User-Agent': 'ReconX Security Scanner'}
            )
            
            # Analyze headers
            analysis = analyze_headers(response.headers)
            
            results[url] = {
                'status_code': response.status_code,
                'headers_found': analysis['found'],
                'headers_missing': analysis['missing'],
                'security_score': analysis['score'],
                'recommendations': analysis['recommendations']
            }
            
            if not silent:
                print(f"      Security Score: {analysis['score']}/7")
            
        except requests.exceptions.RequestException as e:
            if not silent:
                print(f"      Error: {str(e)}")
            results[url] = {
                'error': str(e)
            }
            continue
        except Exception as e:
            if not silent:
                print(f"      Unexpected error: {str(e)}")
            continue
    
    # Save results
    if results:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate summary report
        generate_header_summary(results, output_dir)
    
    return results


def analyze_headers(headers):
    """
    Analyze response headers for security
    """
    found = {}
    missing = []
    recommendations = []
    
    for header, name in SECURITY_HEADERS.items():
        if header in headers:
            found[name] = headers[header]
        else:
            missing.append(name)
            recommendations.append(f"Add {name} header")
    
    score = len(found)
    
    # Additional checks
    if 'X-Powered-By' in headers:
        recommendations.append("Remove X-Powered-By header (information disclosure)")
    
    if 'Server' in headers:
        recommendations.append(f"Consider hiding/obfuscating Server header: {headers['Server']}")
    
    return {
        'found': found,
        'missing': missing,
        'score': score,
        'recommendations': recommendations
    }


def generate_header_summary(results, output_dir):
    """
    Generate text summary of security headers
    """
    summary_file = Path(output_dir) / "security_headers_summary.txt"
    
    with open(summary_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("SECURITY HEADERS ANALYSIS SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        
        for url, data in results.items():
            if 'error' in data:
                f.write(f"\n[!] {url}\n")
                f.write(f"    Error: {data['error']}\n")
                continue
            
            f.write(f"\n[*] {url}\n")
            f.write(f"    Status: {data['status_code']}\n")
            f.write(f"    Security Score: {data['security_score']}/7\n")
            
            if data['headers_missing']:
                f.write(f"    Missing Headers: {', '.join(data['headers_missing'])}\n")
            
            if data['recommendations']:
                f.write(f"    Recommendations:\n")
                for rec in data['recommendations']:
                    f.write(f"      - {rec}\n")
            
            f.write("\n" + "-" * 70 + "\n")