"""
CSC368H1: Assignment 3, Part 2
"""

import m5
from m5.objects import *

import argparse


CSC368H1_DIR = "/u/csc368h/fall/pub"
MIBENCH_SRC_DIR = f"{CSC368H1_DIR}/gem5-workloads/src/mibench"
MIBENCH_BIN_DIR = f"{CSC368H1_DIR}/gem5-workloads/bin/mibench"


##############################################################################
# Argument parsing
##############################################################################
parser = argparse.ArgumentParser()
parser.add_argument("benchmark", type=str)
parser.add_argument("-o", "--out_dir", type=str, default="m5out")

# Parse command-line arguments
args = parser.parse_args()


##############################################################################
# MIBench workloads
##############################################################################
class KernelDaxpySmall(Process):
    executable = f"{CSC368H1_DIR}/gem5-workloads/bin/daxpy"
    cmd = [
        f"{CSC368H1_DIR}/gem5-workloads/bin/daxpy",
        f"1000",
    ]


class MIBenchBasicmathSmall(Process):
    executable = f"{MIBENCH_BIN_DIR}/basicmath_small"
    cmd = [
        f"{MIBENCH_BIN_DIR}/basicmath_small",
    ]


class MIBenchBasicmath(Process):
    executable = f"{MIBENCH_BIN_DIR}/basicmath_large"
    cmd = [
        f"{MIBENCH_BIN_DIR}/basicmath_large",
    ]


class MIBenchBitcountsSmall(Process):
    executable = f'{MIBENCH_BIN_DIR}/bitcnts'
    cmd = [
        f'{MIBENCH_BIN_DIR}/bitcnts',
        '75000'
    ]


class MIBenchBitcounts(Process):
    executable = f'{MIBENCH_BIN_DIR}/bitcnts'
    cmd = [
        f'{MIBENCH_BIN_DIR}/bitcnts',
        '1125000'
    ]


class MIBenchQsortSmall(Process):
    executable = f'{MIBENCH_BIN_DIR}/qsort_small'
    cmd = [
        f'{MIBENCH_BIN_DIR}/qsort_small',
        f'{MIBENCH_SRC_DIR}/automotive/qsort/input_small.dat',
    ]


class MIBenchQsort(Process):
    executable = f'{MIBENCH_BIN_DIR}/qsort_large'
    cmd = [
        f'{MIBENCH_BIN_DIR}/qsort_large',
        f'{MIBENCH_SRC_DIR}/automotive/qsort/input_large.dat',
    ]


class MIBenchSusanEdgesSmall(Process):
    executable = f'{MIBENCH_BIN_DIR}/susan'
    cmd = [
        f'{MIBENCH_BIN_DIR}/susan',
        f'{MIBENCH_SRC_DIR}/automotive/susan/input_small.pgm',
        f'{args.out_dir}/output_small.edges.pgm',
        '-e'
    ]


class MIBenchSusanSmoothingSmall(Process):
    executable = f'{MIBENCH_BIN_DIR}/susan'
    cmd = [
        f'{MIBENCH_BIN_DIR}/susan',
        f'{MIBENCH_SRC_DIR}/automotive/susan/input_small.pgm',
        f'{args.out_dir}/output_small.smoothing.pgm',
        '-s'
    ]


class MIBenchSusanCornersSmall(Process):
    executable = f'{MIBENCH_BIN_DIR}/susan'
    cmd = [
        f'{MIBENCH_BIN_DIR}/susan',
        f'{MIBENCH_SRC_DIR}/automotive/susan/input_small.pgm',
        f'{args.out_dir}/output_small.corners.pgm',
        '-c'
    ]


class MIBenchSusanEdges(Process):
    executable = f'{MIBENCH_BIN_DIR}/susan'
    cmd = [
        f'{MIBENCH_BIN_DIR}/susan',
        f'{MIBENCH_SRC_DIR}/automotive/susan/input_large.pgm',
        f'{args.out_dir}/output_large.edges.pgm',
        '-e'
    ]


class MIBenchSusanSmoothing(Process):
    executable = f'{MIBENCH_BIN_DIR}/susan'
    cmd = [
        f'{MIBENCH_BIN_DIR}/susan',
        f'{MIBENCH_SRC_DIR}/automotive/susan/input_large.pgm',
        f'{args.out_dir}/output_large.smoothing.pgm',
        '-s'
    ]


class MIBenchSusanCorners(Process):
    executable = f'{MIBENCH_BIN_DIR}/susan'
    cmd = [
        f'{MIBENCH_BIN_DIR}/susan',
        f'{MIBENCH_SRC_DIR}/automotive/susan/input_large.pgm',
        f'{args.out_dir}/output_large.corners.pgm',
        '-c'
    ]


class MIBenchJpegEncodeSmall(Process):
    executable = f'{MIBENCH_BIN_DIR}/cjpeg'
    cmd = [
        f'{MIBENCH_BIN_DIR}/cjpeg',
        '-dct', 'int',
        '-progressive',
        '-optimize',
        '-outfile', f'{args.out_dir}/output_small_encode.jpeg',
        f'{MIBENCH_SRC_DIR}/consumer/jpeg/input_small.ppm'
    ]


class MIBenchJpegEncode(Process):
    executable = f'{MIBENCH_BIN_DIR}/cjpeg'
    cmd = [
        f'{MIBENCH_BIN_DIR}/cjpeg',
        '-dct', 'int',
        '-progressive',
        '-optimize',
        '-outfile', f'{args.out_dir}/output_large_encode.jpeg',
        f'{MIBENCH_SRC_DIR}/consumer/jpeg/input_large.ppm'
    ]

 
class MIBenchJpegDecodeSmall(Process):
    executable = f'{MIBENCH_BIN_DIR}/djpeg'
    cmd = [
        f'{MIBENCH_BIN_DIR}/djpeg',
        '-dct', 'int',
        '-ppm',
        '-outfile', f'{args.out_dir}/output_small_decode.ppm',
        f'{MIBENCH_SRC_DIR}/consumer/jpeg/input_small.jpg'
    ]


class MIBenchJpegDecode(Process):
    executable = f'{MIBENCH_BIN_DIR}/djpeg'
    cmd = [
        f'{MIBENCH_BIN_DIR}/djpeg',
        '-dct', 'int',
        '-ppm',
        '-outfile', f'{args.out_dir}/output_large_decode.ppm',
        f'{MIBENCH_SRC_DIR}/consumer/jpeg/input_large.jpg'
    ]


class MIBenchDijkstraSmall(Process):
    executable = f"{MIBENCH_BIN_DIR}/dijkstra_small"
    cmd = [
        f"{MIBENCH_BIN_DIR}/dijkstra_small",
        f"{MIBENCH_SRC_DIR}/network/dijkstra/input.dat",
    ]


class MIBenchDijkstra(Process):
    executable = f"{MIBENCH_BIN_DIR}/dijkstra_large"
    cmd = [
        f"{MIBENCH_BIN_DIR}/dijkstra_large",
        f"{MIBENCH_SRC_DIR}/network/dijkstra/input.dat",
    ]


MIBenchWorkloads = {
    "daxpy_small": KernelDaxpySmall(),
    "basicmath_small": MIBenchBasicmathSmall(),
    "basicmath": MIBenchBasicmath(),
    "bitcounts_small": MIBenchBitcountsSmall(),
    "bitcounts": MIBenchBitcounts(),
    "qsort_small":MIBenchQsortSmall(),
    "qsort": MIBenchQsort(),
    'susan_edges_small': MIBenchSusanEdgesSmall(),
    'susan_smoothing_small': MIBenchSusanSmoothingSmall(),
    'susan_corners_small': MIBenchSusanCornersSmall(),
    'susan_edges': MIBenchSusanEdges(),
    'susan_smoothing': MIBenchSusanSmoothing(),
    'susan_corners': MIBenchSusanCorners(),
    'jpeg_encode_small': MIBenchJpegEncodeSmall(),
    'jpeg_encode': MIBenchJpegEncode(),
    'jpeg_decode_small': MIBenchJpegDecodeSmall(),
    'jpeg_decode': MIBenchJpegDecode(),
    "dijkstra_small": MIBenchDijkstraSmall(),
    "dijkstra": MIBenchDijkstra(),
}


##############################################################################
# System creation
##############################################################################
system = System()
system.mem_mode = "atomic"

# gem5 needs to know the clock and voltage
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()  # defaults to 1V

# Create a crossbar so that we can connect main memory and the CPU (below)
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

# CPU Setup
# system.cpu = X86TimingSimpleCPU()
system.cpu = X86AtomicSimpleCPU()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# This is needed when we use x86 CPUs
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# See Assignment 3 handout
system.cache_line_size = 64

# Setup main memory to be "ideal" (this is not realistic)
system.mem_ctrl = SimpleMemory()
system.mem_ctrl.port = system.membus.mem_side_ports
system.mem_ctrl.latency = "1ns"
system.mem_ctrl.bandwidth = "0B/s"

address_ranges = [AddrRange("8GiB")]
system.mem_ranges = address_ranges

process = MIBenchWorkloads[args.benchmark]
system.workload = SEWorkload.init_compatible(process.executable)
system.cpu.workload = process
system.cpu.createThreads()


##############################################################################
# Start the simulation
##############################################################################
root = Root(full_system=False, system=system)  # must assign a root

m5.instantiate()  # must be called before m5.simulate
m5.simulate()

print("End of simulation")
