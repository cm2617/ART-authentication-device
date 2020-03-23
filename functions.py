# Importing general libraries
import numpy as np
import matplotlib.pyplot as plt

# Importing libraries for ADC and DAC
# import board
# import busio
# import adafruit_mcp4725

# #i2c = busio.I2C(board.SCL, board.SDA)   # Setting up i2c

# dac = adafruit_mcp4725.MCP4725(i2c) # Setting up DAC

# ads = ADS.ADS1115(i2c)  # Setting up ADC
# chan = AnalogIn(ads, ADS.P0, ADS.P1)
# ads.gain = 2/3

from smbus2 import SMBus    # i2c library used for i2c with LMP91000

# from Adafruit_CharLCD import Adafruit_CharLCD
#lcd = Adafruit_CharLCD(rs = 26, en = 19, d4 = 13, d5 = 6, d6 = 5, d7 = 11, cols = 16, lines = 2)
lcd.clear()

def initialise(startPotential, endPotential, stepSize, amplitude):

    lcd.message('  INITIALISING \n   THE DEVICE') 

    # Generating staircase wave
    stair = np.arange(startPotential, endPotential, stepSize)
    stair = np.repeat(stair, 2)  # duplicating values

    # Generating squarewave
    square = []
    for i in range(len(stair)):
        if i%2 ==0:
            square.append(amplitude)
        else:
            square.append(-1*amplitude)

    # Adding staircase and squarewave 
    excitationVoltage = np.add(stair, square)

    vref = [] # Vref needed to be fed into LMP91000
    refcn = ['0b101'] * len(excitationVoltage) # Byte needed to be fed into LMP91000
    for idx, iter in enumerate(excitationVoltage):
        absIter = np.abs(iter)
        if iter > 0:
            refcn[idx] = refcn[idx] + '1'
        if iter < 0:
            refcn[idx] = refcn[idx] + '0'

        if absIter < 0.015:
            vref.append(1.5)
            refcn[idx] = refcn[idx] + '0000'

        if (absIter >= 0.015) & (absIter <= 0.05):
            vref.append(round(absIter*100,2))
            refcn[idx] = refcn[idx] + '0001'

        if (absIter > 0.05) & (absIter <= 0.1):
            vref.append(round(absIter*50,2))
            refcn[idx] = refcn[idx] + '0010'

        if (absIter > 0.1) & (absIter <= 0.2):
            vref.append(round(absIter*25,2))
            refcn[idx] = refcn[idx] + '0011'

        if (absIter > 0.2) & (absIter <= 0.32):
            vref.append(round(absIter*10,2))
            refcn[idx] = refcn[idx] + '0110'

    refcn_decimal = []  # Converting the binary back into decimal
    for ele in refcn:
        refcn_decimal.append(int(ele, 2))


    print(excitationVoltage)
    print(vref)

    vref_bit = []   # Converting Vref into bits for DAC
    for ele in vref:
        vref_bit.append(to_bit(ele))

    
    lcd.message('     DEVICE\n     IS READY')    

    # plt.plot(stair)
    # plt.plot(square)
    # plt.plot(excitationVoltage)
    # plt.show()

    return vref_bit, refcn_decimal,excitationVoltage

# def to_bit(vref):
#     # Converting Vref to bit version (0-12 bits)
#     return int(round(vref/(5/4096)))-1

def outputExcitationAndMeasure(vref_bit,refcn_decimal, quietTime, frequency):
    period = 1/frequency
    measured = []

    time.sleep(quietTime)
    for i in range(len(vref_bit)):
        dac.raw_value = vref_bit[i]
        with SMBus(1) as bus:
            data = refcn_decimal[i]
            bus.write_byte_data(0x48, 0x11, data)
        time.sleep(period/2)
        #measured.append(chan.voltage)

    return measured









