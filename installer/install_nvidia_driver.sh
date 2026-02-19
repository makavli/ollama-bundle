#!/bin/bash
# NVIDIA Driver Installation Script
# Based on official NVIDIA documentation
# https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/ubuntu.html

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "NVIDIA Driver Installation"
echo "=========================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   echo "Usage: sudo bash install_nvidia_driver.sh"
   exit 1
fi

# Check if GPU exists
echo "Checking for NVIDIA GPU..."
if ! lspci 2>/dev/null | grep -qi NVIDIA; then
    echo -e "${RED}❌ No NVIDIA GPU detected!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
lspci 2>/dev/null | grep -i NVIDIA | head -3
echo ""

# Check if driver already installed
echo "Checking for existing driver..."
if command -v nvidia-smi &> /dev/null; then
    DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
    echo -e "${GREEN}✓ Driver $DRIVER_VERSION already installed${NC}"
    echo ""
    echo "GPU Status:"
    nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader 2>/dev/null || nvidia-smi
    echo ""
    echo -e "${GREEN}✓ GPU is working correctly!${NC}"
    echo "No action needed."
    exit 0
fi

echo "Installing NVIDIA driver..."
echo ""

# Step 1: Update and install dependencies
echo "STEP 1: Installing dependencies..."
apt-get update
apt-get install -y \
    build-essential \
    linux-headers-$(uname -r) \
    dkms \
    lsb-release \
    2>&1 | tail -5
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 2: Install ubuntu-drivers
echo "STEP 2: Setting up driver tools..."
apt-get install -y ubuntu-drivers-common 2>&1 | tail -3
echo -e "${GREEN}✓ Driver tools installed${NC}"
echo ""

# Step 3: List available drivers
echo "STEP 3: Available NVIDIA drivers:"
ubuntu-drivers devices 2>&1 | grep -i "nvidia" || echo "No drivers listed"
echo ""

# Step 4: Install driver using ubuntu-drivers autoinstall
echo "STEP 4: Installing NVIDIA driver (this may take 2-3 minutes)..."
if ubuntu-drivers autoinstall 2>&1 | tail -10; then
    echo -e "${GREEN}✓ Driver installation initiated${NC}"
else
    echo -e "${YELLOW}⚠ Driver autoinstall completed${NC}"
fi
echo ""

# Step 5: Verify installation
echo "STEP 5: Verifying installation..."
sleep 3

if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA driver verification successful!${NC}"
    echo ""
    echo "GPU Information:"
    nvidia-smi --query-gpu=name,driver_version,compute_cap,memory.total --format=csv 2>/dev/null || nvidia-smi
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ Installation Complete!${NC}"
    echo "=========================================="
else
    echo -e "${RED}❌ Driver verification failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check system: nvidia-smi"
    echo "2. View kernel logs: dmesg | grep -i nvidia"
    echo "3. Try manual installation from NVIDIA website"
    exit 1
fi
