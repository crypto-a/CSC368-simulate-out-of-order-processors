#!/bin/bash
set -e

# =========================================================================
# CSC368 gem5 Simulation Runner (Placeholder)
# =========================================================================
# This is a placeholder script for running gem5 simulations locally.
# On the actual droplet, use /root/run_simulation.sh instead.
# =========================================================================

# Load environment variables from .env if it exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from .env..."
    source "$ENV_FILE"
    echo "✓ Environment loaded"
    echo ""
else
    echo "⚠️  No .env file found. Using defaults."
    echo "   Copy .env.sample to .env and configure for your environment."
    echo ""
fi

# Set defaults if not already set by .env
GEM5_BIN="${GEM5_BIN:-/opt/gem5/build/X86/gem5.opt}"
GEM5_HOME="${GEM5_HOME:-/opt/gem5}"
RESULTS_DIR="${RESULTS_DIR:-./simulation_results}"
CPU_TYPE="${CPU_TYPE:-O3CPU}"
L1D_SIZE="${L1D_SIZE:-64kB}"
L1I_SIZE="${L1I_SIZE:-32kB}"
L2_SIZE="${L2_SIZE:-256kB}"
CACHELINE_SIZE="${CACHELINE_SIZE:-64}"

echo "========================================================================="
echo "  CSC368 Out-of-Order Processor Simulation"
echo "========================================================================="
echo ""
echo "Simulation Configuration:"
echo "  - gem5 Binary: $GEM5_BIN"
echo "  - Architecture: X86"
echo "  - CPU Type: $CPU_TYPE"
echo "  - L1 Data Cache: $L1D_SIZE"
echo "  - L1 Instruction Cache: $L1I_SIZE"
echo "  - L2 Cache: $L2_SIZE"
echo "  - Cache Line Size: $CACHELINE_SIZE bytes"
echo ""
echo "========================================================================="
echo ""

# Check if gem5 binary exists

if [ ! -f "$GEM5_BIN" ]; then
    echo "⚠️  gem5 binary not found at: $GEM5_BIN"
    echo ""
    echo "This script is a placeholder for local development."
    echo ""
    echo "To run actual simulations:"
    echo "  1. Deploy infrastructure: cd terraform && terraform apply"
    echo "  2. SSH to droplet: ssh root@<droplet-ip>"
    echo "  3. Run simulation: /root/run_simulation.sh"
    echo ""
    echo "For testing in this devcontainer, you would need to:"
    echo "  - Install gem5 dependencies"
    echo "  - Build gem5 (takes 30-60 minutes)"
    echo "  - Configure simulation parameters"
    echo ""
    echo "See README.md for full setup instructions."
    echo ""
    exit 1
fi

# If gem5 exists, run a sample simulation
echo "Running simulation..."
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_RESULTS_DIR="$RESULTS_DIR/$TIMESTAMP"
mkdir -p "$RUN_RESULTS_DIR"

cd "$GEM5_HOME"

# Example simulation - customize as needed
$GEM5_BIN \
    configs/example/se.py \
    --cmd=/bin/ls \
    --cpu-type=$CPU_TYPE \
    --caches \
    --l2cache \
    --l1d_size=$L1D_SIZE \
    --l1i_size=$L1I_SIZE \
    --l2_size=$L2_SIZE \
    --cacheline_size=$CACHELINE_SIZE \
    2>&1 | tee "$RUN_RESULTS_DIR/simulation.log"

# Copy results
if [ -d "m5out" ]; then
    cp -r m5out/* "$RUN_RESULTS_DIR/"
fi

echo ""
echo "========================================================================="
echo "  Simulation Complete!"
echo "  Results saved to: $RUN_RESULTS_DIR"
echo "========================================================================="
echo ""
echo "View statistics: cat $RUN_RESULTS_DIR/stats.txt"
echo "View config: cat $RUN_RESULTS_DIR/config.ini"
echo ""
