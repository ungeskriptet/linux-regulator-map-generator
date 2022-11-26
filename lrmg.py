#!/usr/bin/env python
# SPDX-License-Identifier: GPL-2.0-only

import argparse
import os
from fdt2 import Fdt2

if os.path.exists("regulators.dtsi"):
    os.remove("regulators.dtsi")

parser = argparse.ArgumentParser(
    description="Generate a device tree regulator map for Qualcomm platfroms based on downstream device tree")
parser.add_argument('dtb', type=argparse.FileType('rb'), help="Device tree blob to parse")
args = parser.parse_args()

def find(fdt: Fdt2):
    for regs in fdt.find_by_compatible('qcom,rpmh-vrm-regulator'):
        for sub in fdt.subnodes(regs):
            yield sub

def get_voltages(fdt: Fdt2, offset):
    min = fdt.getprop_uint32(offset, 'regulator-min-microvolt')
    max = fdt.getprop_uint32(offset, 'regulator-max-microvolt')
    return min, max

def generate(voltages):
    with open('regulators.dtsi', 'a') as f:
        f.write(f'''\
vreg {{
    regulator-min-microvolt = <{voltages[0]}>
    regulator-max-microvolt = <{voltages[1]}>
}}\n
''')

with args.dtb as f:
    print(f"Parsing: {f.name}")
    fdt = Fdt2(f.read())

    found = False
    for offset in find(fdt):
        voltages = get_voltages(fdt, offset)
        generate(voltages)
        found = True

    if not found:
        print(f'{f.name} does not contain any usable regulators')

with open('regulators.dtsi', "r+") as f:
    stripped = f.read().rstrip()
    f.write(stripped)