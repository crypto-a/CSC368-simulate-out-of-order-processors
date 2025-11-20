#!/bin/bash
# Setup script for compiling MIBench workloads on remote VM
# This script is called by Terraform after gem5 installation

set -e

echo "===== Setting up MIBench workloads ====="

# First, build gem5 m5 utility library
echo "===== Building gem5 m5 utility library ====="

# In gem5 v25+, m5 utility needs to be built with scons from the util/m5 directory
cd /opt/gem5/util/m5

# Try to build m5 for x86_64
if [ -f "SConstruct" ]; then
  echo "Building m5 using scons..."
  scons build/x86/out/m5
elif [ -d "src" ]; then
  echo "Building m5 from source directory..."
  cd src
  make
  cd ..
else
  echo "Using pre-built m5 or building with alternate method..."
  # Some gem5 versions build m5 as part of main build
  cd /opt/gem5
  scons build/x86/m5/m5 || echo "m5 may already be built"
  cd util/m5
fi

echo "m5 library build complete or using existing build"

# Create directories for gem5 headers and libraries
sudo mkdir -p /usr/local/include
sudo mkdir -p /usr/local/lib

# Copy entire gem5 include directory to preserve directory structure
if [ -d "/opt/gem5/include/gem5" ]; then
  sudo cp -r /opt/gem5/include/gem5 /usr/local/include/
  echo "Copied gem5 include directory"
elif [ -d "/opt/gem5/include" ]; then
  sudo cp -r /opt/gem5/include/* /usr/local/include/
  echo "Copied all gem5 headers"
else
  echo "Warning: gem5 include directory not found"
fi

# Copy m5 library - try multiple possible locations
if [ -f "/opt/gem5/util/m5/build/x86/out/libm5.a" ]; then
  sudo cp /opt/gem5/util/m5/build/x86/out/libm5.a /usr/local/lib/
elif [ -f "/opt/gem5/util/m5/libm5.a" ]; then
  sudo cp /opt/gem5/util/m5/libm5.a /usr/local/lib/
elif [ -f "/opt/gem5/build/x86/m5/libm5.a" ]; then
  sudo cp /opt/gem5/build/x86/m5/libm5.a /usr/local/lib/
else
  echo "Warning: libm5.a not found - trying to create from object files"
  # Try to find m5.o and create library from it
  M5_OBJ=$(find /opt/gem5 -name "m5.o" -o -name "m5ops*.o" | head -1)
  if [ -n "$M5_OBJ" ]; then
    sudo ar rcs /usr/local/lib/libm5.a $M5_OBJ
  fi
fi

echo "gem5 m5 library installation complete"
ls -la /usr/local/include/gem5/
ls -la /usr/local/lib/libm5.a 2>/dev/null || echo "Warning: libm5.a may not be installed"

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