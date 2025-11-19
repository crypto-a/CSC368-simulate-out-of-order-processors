#!/bin/bash
# retrieve_data.sh
# Script to retrieve simulation data from remote VM to local machine
# Can be run by Terraform or manually

set -e

# Default values (can be overridden by environment variables)
VM_USER="${VM_USER:-}"
VM_HOST="${VM_HOST:-}"
VM_PASSWORD="${VM_PASSWORD:-}"
SSH_PORT="${SSH_PORT:-22}"
REMOTE_DATA_DIR="${REMOTE_DATA_DIR:-~/CSC368-simulate-out-of-order-processors/data/part4}"
LOCAL_DATA_DIR="${LOCAL_DATA_DIR:-./data/part4}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "  Retrieving Simulation Data"
echo "======================================"

# Check if required variables are set
if [ -z "$VM_USER" ] || [ -z "$VM_HOST" ]; then
    echo -e "${RED}ERROR: VM_USER and VM_HOST must be set${NC}"
    echo "Usage:"
    echo "  VM_USER=user VM_HOST=vm-address ./scripts/retrieve_data.sh"
    echo "Or set environment variables:"
    echo "  export VM_USER=user"
    echo "  export VM_HOST=vm-address"
    echo "  ./scripts/retrieve_data.sh"
    exit 1
fi

# Create local data directory
echo -e "${YELLOW}Creating local directory: $LOCAL_DATA_DIR${NC}"
mkdir -p "$LOCAL_DATA_DIR"

# Build scp command
SCP_CMD="scp -r -P $SSH_PORT"

# If password is provided, use sshpass (optional)
if [ -n "$VM_PASSWORD" ] && command -v sshpass &> /dev/null; then
    SCP_CMD="sshpass -p '$VM_PASSWORD' $SCP_CMD"
    echo -e "${YELLOW}Using sshpass for authentication${NC}"
fi

# Construct full remote path
REMOTE_PATH="${VM_USER}@${VM_HOST}:${REMOTE_DATA_DIR}/*"

echo -e "${YELLOW}Copying data from: $REMOTE_PATH${NC}"
echo -e "${YELLOW}Copying data to:   $LOCAL_DATA_DIR${NC}"

# Execute scp command
if $SCP_CMD "$REMOTE_PATH" "$LOCAL_DATA_DIR/" 2>&1; then
    echo -e "${GREEN}✓ Data retrieval successful!${NC}"

    # Count stats files
    STATS_COUNT=$(find "$LOCAL_DATA_DIR" -name "stats.txt" 2>/dev/null | wc -l | tr -d ' ')
    echo -e "${GREEN}✓ Retrieved $STATS_COUNT stats.txt files${NC}"

    # Check for logs
    if [ -f "$LOCAL_DATA_DIR/master_log.txt" ]; then
        echo -e "${GREEN}✓ Master log retrieved${NC}"
    fi

    if [ -f "$LOCAL_DATA_DIR/status.json" ]; then
        echo -e "${GREEN}✓ Status file retrieved${NC}"
        echo ""
        echo "Status summary:"
        cat "$LOCAL_DATA_DIR/status.json" | grep -E '"(completed|failed|total_simulations)"' || true
    fi

    echo ""
    echo "Data saved to: $LOCAL_DATA_DIR/"
    echo ""
    echo "Directory structure:"
    ls -lh "$LOCAL_DATA_DIR/" | head -10

    exit 0
else
    echo -e "${RED}✗ Data retrieval failed${NC}"
    echo ""
    echo "If this failed, you can manually retrieve data with:"
    echo "  scp -r -P $SSH_PORT ${VM_USER}@${VM_HOST}:${REMOTE_DATA_DIR} $LOCAL_DATA_DIR"
    echo ""
    echo "Or SSH into the VM and check if data exists:"
    echo "  ssh -p $SSH_PORT ${VM_USER}@${VM_HOST}"
    echo "  ls -la ${REMOTE_DATA_DIR}"

    exit 1
fi