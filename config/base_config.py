#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSC368 Out-of-Order Processor Simulation Configuration
Base configuration template for Design Space Exploration
"""

import argparse
import sys
import os

# Add gem5 paths
import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal, warn

# Add common configurations path
addToPath('/opt/gem5/configs')
from common import Options, Simulation, CacheConfig, CpuConfig, MemConfig
from common.Caches import *

def create_extended_fupool():
    """Create Extended Functional Unit Pool configuration"""
    fupool = FUPool()

    # Integer ALUs - Extended configuration
    fupool.FUList = [
        IntALU(count=4),  # 4 Integer ALUs
        IntMultDiv(count=2),  # 2 Integer Multiply/Divide units
        FP_ALU(count=2),  # 2 FP ALUs
        FP_MultDiv(count=1),  # 1 FP Multiply/Divide
        ReadPort(count=2),  # 2 Read ports
        WritePort(count=2),  # 2 Write ports
        RdWrPort(count=4),  # 4 Read/Write ports
        IprPort(count=2),  # 2 IPR ports
    ]

    return fupool

def create_aggressive_fupool():
    """Create Aggressive Functional Unit Pool configuration"""
    fupool = FUPool()

    # More functional units for aggressive configuration
    fupool.FUList = [
        IntALU(count=6),  # 6 Integer ALUs
        IntMultDiv(count=3),  # 3 Integer Multiply/Divide units
        FP_ALU(count=3),  # 3 FP ALUs
        FP_MultDiv(count=2),  # 2 FP Multiply/Divide
        ReadPort(count=3),  # 3 Read ports
        WritePort(count=3),  # 3 Write ports
        RdWrPort(count=6),  # 6 Read/Write ports
        IprPort(count=3),  # 3 IPR ports
    ]

    return fupool

def create_system(args):
    """Create the system with configured CPU and memory"""

    # Create the system
    system = System()
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '2GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    # Set memory mode and range
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('2GB')]

    # Create CPU
    if args.cpu_type == 'O3CPU':
        cpu = O3CPU()
    else:
        fatal("Only O3CPU is supported for this configuration")

    # Configure CPU parameters based on design
    if args.design == 'A':
        # Design A: Conservative (820 credits)
        cpu.numROBEntries = 64
        cpu.LQEntries = 8
        cpu.SQEntries = 8
        cpu.fuPool = create_extended_fupool()
        design_name = "Design A (Conservative)"

    elif args.design == 'B':
        # Design B: ROB Focused (960 credits)
        cpu.numROBEntries = 128
        cpu.LQEntries = 8
        cpu.SQEntries = 8
        cpu.fuPool = create_extended_fupool()
        design_name = "Design B (ROB Focused)"

    elif args.design == 'C':
        # Design C: LSQ Focused (1000 credits)
        cpu.numROBEntries = 64
        cpu.LQEntries = 16
        cpu.SQEntries = 16
        cpu.fuPool = create_aggressive_fupool()
        design_name = "Design C (LSQ Focused)"

    else:
        fatal(f"Unknown design: {args.design}")

    print(f"Configuring {design_name}:")
    print(f"  ROB Entries: {cpu.numROBEntries}")
    print(f"  Load Queue Entries: {cpu.LQEntries}")
    print(f"  Store Queue Entries: {cpu.SQEntries}")
    print(f"  FU Pool: {'Aggressive' if args.design == 'C' else 'Extended'}")

    # Set other CPU parameters
    cpu.fetchWidth = 4
    cpu.decodeWidth = 4
    cpu.renameWidth = 4
    cpu.issueWidth = 4
    cpu.wbWidth = 4
    cpu.commitWidth = 4

    # Physical register file sizes
    cpu.numPhysIntRegs = 256
    cpu.numPhysFloatRegs = 256

    # Branch predictor
    cpu.branchPred = TournamentBP()
    cpu.branchPred.BTBEntries = 4096
    cpu.branchPred.localPredictorSize = 2048
    cpu.branchPred.globalPredictorSize = 8192
    cpu.branchPred.choicePredictorSize = 8192

    system.cpu = cpu

    # Create caches
    # L1 caches
    cpu.icache = L1_ICache(size='32kB', assoc=4)
    cpu.dcache = L1_DCache(size='32kB', assoc=4)

    # Connect L1 caches to CPU
    cpu.icache.cpu_side = cpu.icache_port
    cpu.dcache.cpu_side = cpu.dcache_port

    # Create L2 cache
    system.l2cache = L2Cache(size='256kB', assoc=8)

    # Create memory bus
    system.membus = SystemXBar()
    system.l2bus = L2XBar()

    # Connect caches
    cpu.icache.mem_side = system.l2bus.cpu_side_ports
    cpu.dcache.mem_side = system.l2bus.cpu_side_ports
    system.l2cache.cpu_side = system.l2bus.mem_side_ports
    system.l2cache.mem_side = system.membus.cpu_side_ports

    # Create interrupt controller
    cpu.createInterruptController()

    # Create memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Connect system port
    system.system_port = system.membus.cpu_side_ports

    # Create process
    process = Process()
    process.cmd = [args.binary] + args.options.split() if args.options else [args.binary]
    cpu.workload = process
    cpu.createThreads()

    return system

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='CSC368 Out-of-Order Processor Simulation')

    parser.add_argument('--design', type=str, required=True,
                       choices=['A', 'B', 'C'],
                       help='Design configuration (A/B/C)')

    parser.add_argument('--binary', type=str, required=True,
                       help='Binary to execute')

    parser.add_argument('--options', type=str, default='',
                       help='Options to pass to the binary')

    parser.add_argument('--cpu-type', type=str, default='O3CPU',
                       choices=['O3CPU'],
                       help='CPU model (only O3CPU supported)')

    parser.add_argument('--output', type=str, default='m5out',
                       help='Output directory for stats')

    parser.add_argument('--max-inst', type=int, default=0,
                       help='Maximum number of instructions to simulate')

    return parser.parse_args()

def main():
    """Main simulation function"""
    args = parse_arguments()

    # Set output directory
    m5.options.outdir = args.output

    # Create the system
    print(f"Creating system for {args.design} configuration...")
    system = create_system(args)

    # Create root and instantiate
    root = Root(full_system=False, system=system)
    m5.instantiate()

    print("Beginning simulation...")
    exit_event = m5.simulate(args.max_inst)

    print(f"Simulation ended: {exit_event.getCause()}")
    print(f"Simulated ticks: {m5.curTick()}")

    # Print some basic stats
    print("\nBasic Statistics:")
    print(f"  Simulated instructions: {system.cpu.commitStats0.numInsts}")
    print(f"  Simulated cycles: {system.cpu.numCycles}")
    if system.cpu.numCycles > 0:
        ipc = system.cpu.commitStats0.numInsts / system.cpu.numCycles
        print(f"  IPC: {ipc:.4f}")

if __name__ == "__main__":
    main()