#!/usr/bin/env python3
"""
Design B: ROB-Focused Configuration (960 credits)
- ROB: 128 entries (DOUBLED from Design A)
- Load Queue: 8 entries
- Store Queue: 8 entries
- Functional Units: Extended pool
"""

import m5
from m5.objects import *
from m5.util import addToPath
import sys
import argparse

# Add gem5 configs path
addToPath('/opt/gem5/configs')
from common import Options, Simulation
from common.Caches import *

def create_cpu():
    """Create O3CPU with Design B parameters"""
    cpu = O3CPU()

    # Design B specific parameters (ROB-Focused)
    cpu.numROBEntries = 128  # DOUBLED ROB for more in-flight instructions
    cpu.LQEntries = 8        # Keep Load Queue small
    cpu.SQEntries = 8        # Keep Store Queue small

    # Pipeline widths (standard)
    cpu.fetchWidth = 4
    cpu.decodeWidth = 4
    cpu.renameWidth = 4
    cpu.issueWidth = 4
    cpu.wbWidth = 4
    cpu.commitWidth = 4

    # Physical registers - increased for larger ROB
    cpu.numPhysIntRegs = 320  # Increased for more in-flight instructions
    cpu.numPhysFloatRegs = 320

    # Branch predictor - Tournament
    cpu.branchPred = TournamentBP()
    cpu.branchPred.BTBEntries = 4096
    cpu.branchPred.localPredictorSize = 2048
    cpu.branchPred.globalPredictorSize = 8192
    cpu.branchPred.choicePredictorSize = 8192

    # Extended Functional Unit Pool (same as Design A)
    fu_pool = FUPool()
    fu_pool.FUList = [
        IntALU(opList=[OpDesc(opClass='IntAlu')], count=4),
        IntMultDiv(opList=[OpDesc(opClass='IntMult', opLat=3),
                          OpDesc(opClass='IntDiv', opLat=20)], count=2),
        FP_ALU(opList=[OpDesc(opClass='FloatAdd', opLat=2),
                      OpDesc(opClass='FloatCmp', opLat=2),
                      OpDesc(opClass='FloatCvt', opLat=2)], count=2),
        FP_MultDiv(opList=[OpDesc(opClass='FloatMult', opLat=4),
                          OpDesc(opClass='FloatMultAcc', opLat=5),
                          OpDesc(opClass='FloatDiv', opLat=12),
                          OpDesc(opClass='FloatSqrt', opLat=24)], count=1),
        ReadPort(opList=[OpDesc(opClass='MemRead')], count=2),
        WritePort(opList=[OpDesc(opClass='MemWrite')], count=2),
    ]
    cpu.fuPool = fu_pool

    return cpu

def create_system(binary_path, binary_args=""):
    """Create the complete system"""
    system = System()

    # Clock domain
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '2GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    # Memory setup
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('2GB')]

    # Create CPU
    system.cpu = create_cpu()

    # L1 Caches
    system.cpu.icache = L1_ICache(size='32kB', assoc=4)
    system.cpu.dcache = L1_DCache(size='32kB', assoc=4)

    # Connect L1 caches to CPU
    system.cpu.icache.cpu_side = system.cpu.icache_port
    system.cpu.dcache.cpu_side = system.cpu.dcache_port

    # L2 Cache and bus
    system.l2bus = L2XBar()
    system.l2cache = L2Cache(size='256kB', assoc=8)

    # Connect L1 to L2
    system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
    system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports
    system.l2cache.cpu_side = system.l2bus.mem_side_ports

    # Memory bus and controller
    system.membus = SystemXBar()
    system.l2cache.mem_side = system.membus.cpu_side_ports

    # Memory controller
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # System port
    system.system_port = system.membus.cpu_side_ports

    # Interrupt controller
    system.cpu.createInterruptController()

    # Create process
    process = Process()
    cmd = [binary_path]
    if binary_args:
        cmd.extend(binary_args.split())
    process.cmd = cmd
    system.cpu.workload = process
    system.cpu.createThreads()

    return system

def get_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Design B Configuration')

    parser.add_argument('binary', help='Path to binary to execute')
    parser.add_argument('--args', default='', help='Arguments for binary')
    parser.add_argument('--output', default='m5out/design_b',
                       help='Output directory')
    parser.add_argument('--max-inst', type=int, default=0,
                       help='Maximum instructions to simulate (0=unlimited)')

    return parser.parse_args()

def main():
    args = get_args()

    # Set output directory
    m5.options.outdir = args.output

    print("="*60)
    print("Design B: ROB-Focused Configuration (960 credits)")
    print("="*60)
    print("Configuration:")
    print("  ROB Entries: 128 (DOUBLED)")
    print("  Load Queue: 8")
    print("  Store Queue: 8")
    print("  FU Pool: Extended")
    print("  Physical Registers: 320 (increased)")
    print("  Clock: 2GHz")
    print(f"  Binary: {args.binary}")
    print(f"  Output: {args.output}")
    print("="*60)
    print("Hypothesis: Larger ROB helps compute-heavy workloads")
    print("           (basicmath, bitcount) extract more ILP")
    print("="*60)

    # Create system
    system = create_system(args.binary, args.args)

    # Create root and instantiate
    root = Root(full_system=False, system=system)
    m5.instantiate()

    print("Starting simulation...")
    exit_event = m5.simulate(args.max_inst)

    print(f"\nSimulation complete: {exit_event.getCause()}")
    print(f"Simulated ticks: {m5.curTick()}")

    # Basic stats
    stats = system.cpu.commitStats0
    if hasattr(stats, 'numInsts'):
        print(f"Instructions: {stats.numInsts}")
        if system.cpu.numCycles > 0:
            ipc = stats.numInsts / system.cpu.numCycles
            print(f"IPC: {ipc:.4f}")
            print(f"Cycles: {system.cpu.numCycles}")

if __name__ == "__main__":
    main()