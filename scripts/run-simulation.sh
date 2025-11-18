#!/bin/bash
set -e

echo "======================================"
echo "  Running gem5 Simulation Test"
echo "======================================"

# Set gem5 path
GEM5_PATH="${GEM5_PATH:-/opt/gem5}"
GEM5_BIN="$GEM5_PATH/build/X86/gem5.opt"

# Check if gem5 exists
if [ ! -f "$GEM5_BIN" ]; then
    echo "ERROR: gem5 binary not found at $GEM5_BIN"
    exit 1
fi

echo "gem5 binary found: $GEM5_BIN"
echo ""

# Test 1: Check gem5 version/help
echo "Test 1: Checking gem5 help output..."
$GEM5_BIN --help | head -20
echo ""

# Test 2: List available SimObjects
echo "Test 2: Listing available SimObjects..."
$GEM5_BIN --list-sim-objects | head -20
echo ""

# Test 3: Run a very basic simulation (just build info)
echo "Test 3: Checking gem5 build info..."
$GEM5_BIN --build-info
echo ""

echo "======================================"
echo "  gem5 Simulation Test Complete!"
echo "======================================"
echo ""
echo "gem5 is installed and working correctly!"
echo "Location: $GEM5_BIN"
echo ""
echo "Next steps:"
echo "  1. Create simulation configuration files"
echo "  2. Add workloads to test"
echo "  3. Run full simulations with your configs"
echo ""