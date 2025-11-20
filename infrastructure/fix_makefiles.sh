#!/bin/bash
# Fix all Makefile paths to use /usr/local instead of course infrastructure

set -e

echo "Fixing Makefile paths..."

WORKLOADS_DIR=~/CSC368-simulate-out-of-order-processors/workloads

# Fix basicmath
sed -i 's|-I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib|-I/usr/local/include -L/usr/local/lib|g' \
    $WORKLOADS_DIR/basicmath/Makefile

# Fix bitcount
sed -i 's|-I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib|-I/usr/local/include -L/usr/local/lib|g' \
    $WORKLOADS_DIR/bitcount/Makefile

# Fix qsort
sed -i 's|-I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib|-I/usr/local/include -L/usr/local/lib|g' \
    $WORKLOADS_DIR/qsort/Makefile

# Fix susan
sed -i 's|-I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib|-I/usr/local/include -L/usr/local/lib|g' \
    $WORKLOADS_DIR/susan/Makefile

# Fix jpeg
sed -i 's|-I/u/csc368h/fall/pub/include|-I/usr/local/include|g' \
    $WORKLOADS_DIR/jpeg/jpeg-6a/Makefile

# Fix dijkstra
sed -i 's|-I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib|-I/usr/local/include -L/usr/local/lib|g' \
    $WORKLOADS_DIR/dijkstra/Makefile

echo "All Makefiles fixed!"