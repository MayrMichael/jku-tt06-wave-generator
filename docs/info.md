<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

Wave generator is a project that deals with the generation of various signals. These signals are sine, triangle, sawtooth and square pulse. The desired function can then be selected by applying simple control signals. Each calculated value is generated as a 2-complement in the fixed-point system Q7 and then output accordingly either via the parallel or the serial interface. An SPI interface is used for the serial output, but this can only write.  This makes it possible to connect a DAC to the wave generator and convert the digital signals to analogue signals. 
In general, the signals can be influenced by three parameters: 
- The frequency
- The phase
- The amplitude
Depending on the type of signal, however, certain restrictions on the parameters must be taken into account. 
In addition, the generation frequency of the values is related to the internal clock frequency of the system by a factor of 40. Therefore, a value requires 40 clock pulses to be calculated and output via the serial interface.


### Sine wave
Hello there

## How to test

To test you have to do following

## External hardware

List external hardware used in your project (e.g. PMOD, LED display, etc), if any
