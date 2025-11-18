"""
CSC368H1: Assignment 3 Part 4
"""
import m5
from m5.objects import *

import argparse


CSC368H1_DIR = '/u/csc368h/fall/pub'
MIBENCH_SRC_DIR = f'{CSC368H1_DIR}/gem5-workloads/src/mibench'
MIBENCH_BIN_DIR = f'{CSC368H1_DIR}/gem5-workloads/bin/mibench'


##############################################################################
# Argument parsing
##############################################################################
parser = argparse.ArgumentParser()
parser.add_argument('benchmark', type=str)
parser.add_argument('-o', '--out_dir', type=str, default='m5out')

parser.add_argument('--fetch_buffer_size', type=int, default=64)
parser.add_argument('--fetch_queue_size', type=int, default=4)

parser.add_argument('--fetch_width', type=int, default=1)
parser.add_argument('--decode_width', type=int, default=1)
parser.add_argument('--rename_width', type=int, default=1)
parser.add_argument('--dispatch_width', type=int, default=1)
parser.add_argument('--issue_width', type=int, default=1)
parser.add_argument('--commit_width', type=int, default=1)

parser.add_argument('--num_iq_entries', type=int, default=16)
parser.add_argument('--num_rob_entries', type=int, default=32)
parser.add_argument('--lq_entries', type=int, default=4)
parser.add_argument('--sq_entries', type=int, default=4)

# options are: basic, extended, aggressive
parser.add_argument('--fu_pool', type=str, default='basic')

## Parse command-line arguments
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
# Cache configurations
##############################################################################
class InstructionCache(Cache):
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 8
    tgts_per_mshr = 20
    assoc = 2
    size='4KiB'

    
class DataCache(Cache):
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 8
    tgts_per_mshr = 20
    assoc = 8
    size = '4KiB'


##############################################################################
# System creation
##############################################################################
system = System()
system.mem_mode = 'timing'

## gem5 needs to know the clock and voltage
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain() # defaults to 1V

## Create a crossbar so that we can connect main memory and the CPU (below)
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports

##############################################################################
# CPU
##############################################################################
system.cpu = X86O3CPU(
    cacheStorePorts=1,
    cacheLoadPorts=2,   # EDIT: Fixed on November 13th, 8:36 AM (was 1)
    fetchBufferSize=args.fetch_buffer_size,
    fetchQueueSize=args.fetch_queue_size,
    fetchWidth=args.fetch_width,
    decodeWidth=args.decode_width,
    renameWidth=args.rename_width,
    dispatchWidth=args.dispatch_width,
    issueWidth=args.issue_width,
    commitWidth=args.commit_width,
    numIQEntries=args.num_iq_entries,
    numROBEntries=args.num_rob_entries,
    LQEntries=args.lq_entries,
    SQEntries=args.sq_entries
)

## This is needed when we use x86 CPUs
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

if args.fu_pool == 'basic':
    system.cpu.fuPool = FUPool(
        FUList = [
            IntALU(count=1),
            IntMultDiv(count=1),
            FP_ALU(count=1),
            FP_MultDiv(count=1),
            SIMD_Unit(count=1),
            ReadPort(count=1),
            WritePort(count=1),
            ]
        )
elif args.fu_pool == 'extended':
     system.cpu.fuPool = FUPool(
        FUList = [
            IntALU(count=2),
            IntMultDiv(count=1),
            FP_ALU(count=2),
            FP_MultDiv(count=1),
            SIMD_Unit(count=1),
            ReadPort(count=2),
            WritePort(count=2),
            ]
        )   
elif args.fu_pool == 'aggressive':
     system.cpu.fuPool = FUPool(
        FUList = [
            IntALU(count=4),
            IntMultDiv(count=2),
            FP_ALU(count=4),
            FP_MultDiv(count=2),
            SIMD_Unit(count=2),
            ReadPort(count=4),
            WritePort(count=4),
            ]
        )

##############################################################################
# Cache
##############################################################################
system.cpu.l1i = InstructionCache()
system.cpu.l1i.mem_side = system.membus.cpu_side_ports
system.cpu.l1i.cpu_side = system.cpu.icache_port

system.cpu.l1d = DataCache()
system.cpu.l1d.mem_side = system.membus.cpu_side_ports
system.cpu.l1d.cpu_side = system.cpu.dcache_port

# NOTE: Changing this will change the block_size of your caches, assuming you
#   don't override them above (we recommend just using the parameter below)
system.cache_line_size = 64

##############################################################################
# Main memory
##############################################################################
system.mem_ctrl = MemCtrl()
system.mem_ctrl.port = system.membus.mem_side_ports
system.mem_ctrl.dram = DDR3_1600_8x8()

## A DDR3_1600_8x8 has 8GB of memory, so setup an 8 GB address range
address_ranges = [AddrRange('8GiB')]
system.mem_ranges = address_ranges
system.mem_ctrl.dram.range = address_ranges[0]

##############################################################################
# Workload
##############################################################################
process = MIBenchWorkloads[args.benchmark]
system.workload = SEWorkload.init_compatible(process.executable)
system.cpu.workload = process
system.cpu.createThreads()

##############################################################################
# Start the simulation
##############################################################################
root = Root(full_system=False, system=system) # must assign a root

m5.instantiate() # must be called before m5.simulate
m5.simulate()

print('End of simulation')
