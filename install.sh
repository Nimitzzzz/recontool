#!/bin/bash

echo "================================================"
echo "ReconX Installation Script"
echo "================================================"
echo ""

# Check if running as root (needed for some installations)
if [ "$EUID" -ne 0 ]; then 
    echo "[*] Note: Some installations may require root/sudo privileges"
fi

# Install Python dependencies
echo "[*] Installing Python dependencies..."
pip3 install -r requirements.txt

# Check and install Go (required for subfinder and httpx)
echo ""
echo "[*] Checking Go installation..."
if ! command -v go &> /dev/null; then
    echo "[!] Go is not installed. Installing Go..."
    wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
    export PATH=$PATH:/usr/local/go/bin
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    rm go1.21.5.linux-amd64.tar.gz
else
    echo "[✓] Go is already installed"
fi

# Add Go bin to path
export PATH=$PATH:~/go/bin

# Install subfinder
echo ""
echo "[*] Installing subfinder..."
if ! command -v subfinder &> /dev/null; then
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    echo "[✓] Subfinder installed"
else
    echo "[✓] Subfinder is already installed"
fi

# Install httpx
echo ""
echo "[*] Installing httpx..."
if ! command -v httpx &> /dev/null; then
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    echo "[✓] HTTPx installed"
else
    echo "[✓] HTTPx is already installed"
fi

# Install nmap
echo ""
echo "[*] Installing nmap..."
if ! command -v nmap &> /dev/null; then
    echo "[*] Please install nmap manually:"
    echo "    Ubuntu/Debian: sudo apt-get install nmap"
    echo "    CentOS/RHEL: sudo yum install nmap"
    echo "    macOS: brew install nmap"
else
    echo "[✓] Nmap is already installed"
fi

# Make main script executable
chmod +x reconx.py

echo ""
echo "================================================"
echo "[✓] Installation complete!"
echo "================================================"
echo ""
echo "Usage:"
echo "  ./reconx.py -d example.com"
echo "  ./reconx.py -l targets.txt --headers --ports"
echo ""
echo "For more information, see README.md"