# ReconX - Quick Start Guide (Creaed by me & my friend https://github.com/its-gugugaga)

## SETUP

### Step 1: Clone & Install
```bash
git clone https://github.com/Nimitzzzz/recontool/
chmod +x install.sh reconx.py
chmod +x ./reconx.py
./install.sh
```

### Step 2: Verify Installation
```bash
./reconx.py --help
```

Expected output:
```
usage: reconx.py [-h] (-d DOMAIN | -l LIST) [--ports] [--headers]
                 [--threads THREADS] [-o {txt,json,csv,all}]
                 [--output-dir OUTPUT_DIR] [--silent] [--no-banner]
```

---

## Common Use Cases

### 1. Basic Subdomain Discovery
```bash
./reconx.py -d example.com
```

**Output:**
- `output/example.com_subdomains.txt` - All discovered subdomains
- `output/live_hosts.txt` - Live HTTP/HTTPS endpoints
- `output/report_*.txt` - Summary report

---

### 2. Full Security Assessment
```bash
./reconx.py -d target.com --headers --ports --output all
```

**Output:**
- All subdomain and live host data
- Port scan results (top 100 ports)
- Security headers analysis
- Reports in TXT, JSON, and CSV

---

### 3. Multiple Targets (Bug Bounty)
```bash
# Create targets file
cat > targets.txt << EOF
hackerone.com
bugcrowd.com
intigriti.com
EOF

# Run scan
./reconx.py -l targets.txt --headers --output json
```

---

### 4. Stealth Mode (Low Profile)
```bash
./reconx.py -d target.com --threads 10 --silent
```

Lower thread count = less aggressive = less likely to trigger WAF/IDS

---

### 5. Quick Headers Check Only
```bash
# First get subdomains
./reconx.py -d example.com

# Then check headers on discovered hosts
cat output/live_hosts.txt | while read url; do
  curl -sI "$url" | grep -i "security\|x-frame\|csp\|hsts"
done
```

---

## Bug Bounty Workflow

### Phase 1: Asset Discovery
```bash
# Discover all subdomains
./reconx.py -d target.com --output json

# Review results
cat output/target.com_subdomains.txt | wc -l
cat output/live_hosts.txt
```

### Phase 2: Initial Assessment
```bash
# Check for security issues
./reconx.py -d target.com --headers --ports

# Look for interesting findings
grep "Missing" output/security_headers_summary.txt
grep "8080\|8443" output/ports.json
```

### Phase 3: Detailed Analysis
```bash
# Now manually test interesting endpoints
# - Missing security headers → XSS testing
# - Open unusual ports → Service enumeration
# - Admin subdomains → Access control testing
```

---

## Reading the Output

### Subdomain File (`_subdomains.txt`)
```
example.com
www.example.com
api.example.com
admin.example.com    ← Interesting!
dev.example.com      ← Interesting!
staging.example.com  ← Interesting!
```

**Look for:**
- `admin`, `dev`, `staging`, `test` - Often misconfigured
- `api`, `rest`, `graphql` - API endpoints
- `old`, `backup`, `legacy` - Forgotten systems

---

### Live Hosts (`live_hosts.json`)
```json
{
  "url": "https://admin.example.com",
  "status_code": 200,
  "title": "Admin Panel",      ← Clear purpose
  "tech": ["PHP", "Apache"],   ← Technology stack
  "content_length": 3421
}
```

**Look for:**
- Status 200 on admin panels
- Exposed technologies (version numbers)
- Login pages without rate limiting

---

### Security Headers (`security_headers_summary.txt`)
```
[*] https://example.com
    Status: 200
    Security Score: 2/7              ← Low score!
    Missing Headers: HSTS, CSP, X-Frame-Options, ...
    Recommendations:
      - Add CSP header
      - Remove X-Powered-By header  ← Info disclosure
```

**Look for:**
- Score < 4/7 → Poor security posture
- Missing CSP → Potential XSS
- Missing X-Frame-Options → Clickjacking
- X-Powered-By present → Version disclosure

---

### Port Scan (`ports.json`)
```json
{
  "admin.example.com": [
    {"port": 22, "protocol": "tcp", "service": "ssh"},
    {"port": 3306, "protocol": "tcp", "service": "mysql"},  ← Exposed DB!
    {"port": 8080, "protocol": "tcp", "service": "http-proxy"}
  ]
}
```

**Look for:**
- 22 (SSH) → Brute force target
- 3306 (MySQL), 5432 (PostgreSQL) → Exposed databases
- 8080, 8443 → Development/admin interfaces
- 6379 (Redis), 27017 (MongoDB) → Unprotected NoSQL

---

## Common Mistakes

### DON'T: Scan without authorization
```bash
./reconx.py -d random-company.com  # Illegal!
```

### DO: Get written permission first
```bash
# 1. Check bug bounty program scope
# 2. Get written authorization
# 3. THEN scan
./reconx.py -d authorized-target.com
```

---

### DON'T: Use maximum threads
```bash
./reconx.py -d target.com --threads 500  # Will trigger WAF/IDS!
```

### DO: Start conservative
```bash
./reconx.py -d target.com --threads 25   # Respectful
```

---

### DON'T: Ignore rate limiting
```bash
while true; do ./reconx.py -d target.com; done  # Bad!
```

### DO: Add delays between scans
```bash
./reconx.py -d target.com
sleep 3600  # Wait 1 hour
./reconx.py -d target.com --headers
```

---

## Troubleshooting

### Problem: "subfinder: command not found"
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
export PATH=$PATH:~/go/bin
echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
```

### Problem: "No subdomains found"
**Causes:**
1. Domain doesn't have subdomains
2. Subfinder API keys not configured
3. Network issues

**Solution:**
```bash
# Configure API keys for better results
mkdir -p ~/.config/subfinder
cat > ~/.config/subfinder/config.yaml << EOF
shodan: [YOUR_KEY]
censys: [YOUR_KEY]
virustotal: [YOUR_KEY]
EOF
```

### Problem: "Permission denied" when running nmap
**Cause:** Nmap needs raw socket access for SYN scan

**Solution:**
```bash
# Option 1: Run with sudo (not recommended for full tool)
sudo ./reconx.py -d target.com --ports

# Option 2: Set capabilities on nmap
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

---

## Advanced Tips

### 1. Continuous Monitoring
```bash
#!/bin/bash
# monitor.sh - Run daily reconnaissance

TARGET="example.com"
DATE=$(date +%Y%m%d)

./reconx.py -d $TARGET --output json
mv output/report_*.json reports/$TARGET_$DATE.json

# Compare with yesterday
diff reports/$TARGET_$(date -d yesterday +%Y%m%d).json \
     reports/$TARGET_$DATE.json > changes_$DATE.txt
```

### 2. Integration with Other Tools
```bash
# Send results to Nuclei for vulnerability scanning
./reconx.py -d target.com
nuclei -l output/live_hosts.txt -t ~/nuclei-templates/

# Or to Burp Suite
cat output/live_hosts.txt | while read url; do
  curl -x http://127.0.0.1:8080 "$url"
done
```

### 3. Custom Wordlists
```bash
# Extract discovered subdomains as wordlist
cat output/*_subdomains.txt | \
  cut -d. -f1 | \
  sort -u > custom_wordlist.txt

# Use for future enumeration
```

---

## Learning Resources

### Understanding Subdomain Enumeration
- Why: Expand attack surface, find forgotten assets
- How: DNS records, certificate transparency, web archives
- Tools: Subfinder, Amass, Assetfinder

### Understanding Port Scanning
- Why: Discover running services
- How: TCP/UDP probing
- Tools: Nmap, Masscan

### Understanding Security Headers
- Why: Identify missing security controls
- How: HTTP response analysis
- Reference: https://securityheaders.com/

---

## Red Flags in Output

### High Priority Findings
```
✓ Admin subdomain with no authentication
✓ Development/staging environments in production
✓ Exposed database ports (3306, 5432)
✓ Missing security headers (score < 3)
✓ Old technologies (PHP 5.x, Apache 2.2)
✓ Backup files (backup.example.com)
```

### Medium Priority
```
✓ Self-signed SSL certificates
✓ Information disclosure headers
✓ Non-standard ports open
✓ Partial security headers
```

### Low Priority
```
✓ Minor version information
✓ Default server headers
✓ Standard services (80, 443)
```

---

## Pro Tips

1. **Start Passive**: Run without `--ports` first
2. **Respect Scope**: Only scan what's authorized
3. **Document Everything**: Save all outputs
4. **Iterate**: Recon is not a one-time task
5. **Combine Tools**: ReconX + Manual Testing = Best Results
6. **Stay Updated**: Update tools regularly
7. **Report Responsibly**: Disclose findings properly

---

## Getting Help

- **Documentation**: `README.md`, `docs/TECHNICAL.md`
- **Issues**: GitHub Issues
- **Community**: Security Discord/Slack channels
- **Updates**: `git pull` regularly

---

**Ready to start? Run your first scan:**
```bash
./reconx.py -d example.com
```

**Happy hacking!**
