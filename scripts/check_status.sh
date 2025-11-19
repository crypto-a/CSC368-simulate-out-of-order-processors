#!/bin/bash
# check_status.sh
# Script to check simulation status on remote VM

# Default values
VM_USER="${VM_USER:-}"
VM_HOST="${VM_HOST:-}"
SSH_PORT="${SSH_PORT:-22}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "======================================"
echo "  Simulation Status Checker"
echo "======================================"

# Check if required variables are set
if [ -z "$VM_USER" ] || [ -z "$VM_HOST" ]; then
    echo "ERROR: VM_USER and VM_HOST must be set"
    echo "Usage:"
    echo "  VM_USER=user VM_HOST=vm-address ./scripts/check_status.sh"
    exit 1
fi

echo -e "${YELLOW}Connecting to ${VM_USER}@${VM_HOST}...${NC}"
echo ""

# Check status file
echo -e "${BLUE}=== Status Summary ===${NC}"
ssh -p $SSH_PORT ${VM_USER}@${VM_HOST} "cat ~/CSC368-simulate-out-of-order-processors/data/part4/status.json 2>/dev/null | python3 -m json.tool 2>/dev/null || echo 'Status file not found or invalid JSON'"

echo ""
echo -e "${BLUE}=== Recent Log Entries (last 10) ===${NC}"
ssh -p $SSH_PORT ${VM_USER}@${VM_HOST} "tail -10 ~/CSC368-simulate-out-of-order-processors/data/part4/master_log.txt 2>/dev/null || echo 'Log file not found'"

echo ""
echo -e "${BLUE}=== Stats Files Created ===${NC}"
ssh -p $SSH_PORT ${VM_USER}@${VM_HOST} "find ~/CSC368-simulate-out-of-order-processors/data/part4 -name 'stats.txt' 2>/dev/null | wc -l | xargs echo 'Stats files:' || echo '0'"

echo ""
echo -e "${GREEN}To view full log:${NC}"
echo "  ssh -p $SSH_PORT ${VM_USER}@${VM_HOST} 'tail -f ~/CSC368-simulate-out-of-order-processors/data/part4/master_log.txt'"

echo ""
echo -e "${GREEN}To retrieve data manually:${NC}"
echo "  ./scripts/retrieve_data.sh"
