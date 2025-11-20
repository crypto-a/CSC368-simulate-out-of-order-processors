#!/bin/bash
# Setup script for compiling MIBench workloads on remote VM
# This script is called by Terraform after gem5 installation

set -e

echo "===== Setting up MIBench workloads ====="

# First, build gem5 m5 utility library
echo "===== Building gem5 m5 utility library ====="
cd /opt/gem5/util/m5
# Try modern makefile structure first, fall back to old if needed
if [ -f "Makefile" ]; then
  scons build/x86/out/m5 || (cd src && make)
elif [ -f "Makefile.x86" ]; then
  make -f Makefile.x86
else
  echo "Warning: Could not find m5 Makefile, trying default make"
  make
fi
echo "m5 library built successfully"

# Create directories for gem5 headers and libraries
sudo mkdir -p /usr/local/include/gem5
sudo mkdir -p /usr/local/lib

# Copy m5ops header and library
sudo cp /opt/gem5/include/gem5/m5ops.h /usr/local/include/gem5/
sudo cp /opt/gem5/util/m5/build/x86/out/libm5.a /usr/local/lib/

echo "gem5 m5 library installed to /usr/local"

# Navigate to workloads directory
cd ~/CSC368-simulate-out-of-order-processors/workloads

# Fix all Makefiles to use correct paths
echo "Fixing Makefile paths..."
bash ~/CSC368-simulate-out-of-order-processors/infrastructure/fix_makefiles.sh

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
chmod +x configure 2>/dev/null || true
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