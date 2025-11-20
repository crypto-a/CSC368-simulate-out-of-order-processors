#!/bin/bash
# Setup script for compiling MIBench workloads on remote VM
# This script is called by Terraform after gem5 installation

set -e

echo "===== Setting up MIBench workloads ====="

# Navigate to workloads directory
cd ~/CSC368-simulate-out-of-order-processors/workloads

# Compile each workload
echo "Compiling workloads..."

# Basicmath
echo "  Compiling basicmath..."
cd basicmath
make clean 2>/dev/null || true
make 2>&1 | grep -v "warning:" || true
cd ..

# Bitcount
echo "  Compiling bitcount..."
cd bitcount
make clean 2>/dev/null || true
make 2>&1 | grep -v "warning:" || true
cd ..

# Qsort
echo "  Compiling qsort..."
cd qsort
make clean 2>/dev/null || true
make 2>&1 | grep -v "warning:" || true
cd ..

# Susan
echo "  Compiling susan..."
cd susan
make clean 2>/dev/null || true
make 2>&1 | grep -v "warning:" || true
cd ..

# JPEG - needs special handling (compile inside jpeg-6a subdirectory)
echo "  Compiling jpeg..."
cd jpeg/jpeg-6a
make clean 2>/dev/null || true
./configure --prefix=$(pwd) 2>&1 | grep -v "checking" || true
make 2>&1 | grep -v "warning:" || true
# Binaries (cjpeg, djpeg) will be in jpeg-6a directory
cd ../..

# Dijkstra
echo "  Compiling dijkstra..."
cd dijkstra
make clean 2>/dev/null || true
make 2>&1 | grep -v "warning:" || true
cd ..

echo "===== Workload setup complete ====="
echo "Compiled binaries:"
ls -lh ~/CSC368-simulate-out-of-order-processors/workloads/basicmath/basicmath_* 2>/dev/null || echo "  basicmath: not found"
ls -lh ~/CSC368-simulate-out-of-order-processors/workloads/bitcount/bitcnts 2>/dev/null || echo "  bitcount: not found"
ls -lh ~/CSC368-simulate-out-of-order-processors/workloads/qsort/qsort_* 2>/dev/null || echo "  qsort: not found"
ls -lh ~/CSC368-simulate-out-of-order-processors/workloads/susan/susan 2>/dev/null || echo "  susan: not found"
ls -lh ~/CSC368-simulate-out-of-order-processors/workloads/jpeg/jpeg-6a/cjpeg 2>/dev/null || echo "  jpeg: not found"
ls -lh ~/CSC368-simulate-out-of-order-processors/workloads/jpeg/jpeg-6a/djpeg 2>/dev/null || echo "  jpeg: not found"
ls -lh ~/CSC368-simulate-out-of-order-processors/workloads/dijkstra/dijkstra_* 2>/dev/null || echo "  dijkstra: not found"