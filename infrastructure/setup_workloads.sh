#!/bin/bash
# Setup script for compiling MIBench workloads on remote VM
# This script is called by Terraform after gem5 installation

set -e

echo "===== Setting up MIBench workloads ====="

# Create directory structure
echo "Creating directory structure..."
sudo mkdir -p /u/csc368h/fall/pub/gem5-workloads/src/mibench
sudo mkdir -p /u/csc368h/fall/pub/gem5-workloads/bin/mibench
sudo mkdir -p /u/csc368h/fall/pub/include
sudo mkdir -p /u/csc368h/fall/pub/lib

# Link gem5 headers
echo "Linking gem5 headers..."
sudo cp -r /opt/gem5/include/gem5 /u/csc368h/fall/pub/include/ 2>/dev/null || true

# Create stub m5 library (for workloads without gem5 instrumentation)
echo "Creating m5 stub library..."
cat > /tmp/m5stub.c << 'EOF'
// Stub implementations of m5 ops
void m5_work_begin(long a, long b) {}
void m5_work_end(long a, long b) {}
void m5_reset_stats(long a, long b) {}
void m5_dump_stats(long a, long b) {}
void m5_dump_reset_stats(long a, long b) {}
void m5_checkpoint(long a, long b) {}
void m5_exit(long a) {}
EOF

gcc -c /tmp/m5stub.c -o /tmp/m5stub.o
ar rcs /tmp/libm5.a /tmp/m5stub.o
sudo cp /tmp/libm5.a /u/csc368h/fall/pub/lib/

# Link workload sources
echo "Linking workload sources..."
cd /u/csc368h/fall/pub/gem5-workloads/src/mibench
for dir in ~/CSC368-simulate-out-of-order-processors/workloads/*; do
  if [ -d "$dir" ]; then
    sudo ln -sf "$dir" . 2>/dev/null || true
  fi
done

# Compile workloads
echo "Compiling workloads..."
cd ~/CSC368-simulate-out-of-order-processors/workloads

for workload in basicmath bitcount qsort susan jpeg dijkstra; do
  if [ -d "$workload" ]; then
    echo "  Compiling $workload..."
    cd "$workload"
    make clean 2>/dev/null || true
    make 2>&1 | grep -v "warning:" || echo "  Note: Some warnings during $workload compilation"
    cd ..
  fi
done

# Copy binaries to expected location
echo "Copying binaries..."
find . -type f -executable -name "*_small" -o -name "*_large" -o -name "susan" -o -name "cjpeg" -o -name "djpeg" -o -name "bitcnts" | while read binary; do
  sudo cp "$binary" /u/csc368h/fall/pub/gem5-workloads/bin/mibench/ 2>/dev/null || true
done

echo "===== Workload setup complete ====="
ls -lh /u/csc368h/fall/pub/gem5-workloads/bin/mibench/ | head -20
