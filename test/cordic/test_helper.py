# Copyright 2024 Michael Mayr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE−2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# imports
from bitstring import BitArray
from cocotb.triggers import Timer
from cocotb.binary import BinaryValue, BinaryRepresentation 

def frac2bin(x, sfixed_fract):
    """The method converts a float number into a BinaryValue object

    Args:
        x (float): value to convert
        sfixed_fract (int): fixed-point notation

    Returns:
        BinaryValue: binary twos compliment fixed-point object
    """
    frac_bits = sfixed_fract + 1
    return BinaryValue(value=BitArray(int=int(x * 2**sfixed_fract), length=frac_bits).bin, n_bits=frac_bits, binaryRepresentation=BinaryRepresentation.TWOS_COMPLEMENT )

def unsigned2bin(x, n_bits):
    """The method converts a unsigned int number into a BinaryValue object

    Args:
        x (int): value to convert
        n_bits (int): number of bits

    Returns:
        BinaryValue: binary unsigned value
    """
    return BinaryValue(value=BitArray(uint=x, length=n_bits).bin, n_bits=n_bits)

async def reset_dut(reset_n, duration_ns):
    """Method to reset a dut that is low active

    Args:
        reset_n : low active reset pin of dut
        duration_ns (int): reset duration
    """
    reset_n.value = 0
    await Timer(duration_ns, units="ns")
    reset_n.value = 1
    reset_n._log.info("Reset complete")