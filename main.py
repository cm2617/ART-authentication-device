import numpy as np
import matplotlib.pyplot as plt
from functions import initialise
from functions import outputExcitationAndMeasure
from signal_processing import outlierDeletion, filter, peakdetect
from smbus2 import SMBus

from Adafruit_CharLCD import Adafruit_CharLCD
lcd = Adafruit_CharLCD(rs = 26, en = 19, d4 = 13, d5 = 6, d6 = 5, d7 = 11, cols = 16, lines = 2)
lcd.clear()


# Setting up the LMP91000

with SMBus(1) as bus:
    bus.write_byte_data(0x48, 0x01, 1) # 'Unlocking' the device
    bus.write_byte_data(0x48, 0x012, 3) # 'Unlocking' the device

# Initialising excitation voltage
startPotential = -0.2
endPotential = 0.25
stepSize = 0.008
amplitude = 0.075
vref_bit, refcn_decimal, excitationVoltage = initialise(startPotential, endPotential, stepSize, amplitude)

# Outputing excitation and measuring response signal

quietTime = 5
frequency = 7
measured = outputExcitationAndMeasure(vref_bit, refcn_decimal, quietTime, frequency)

current = (0.5*5 - measured)/350000

# Signal Processing

current = outlierDeletion(current, 3)   # Removing outliers
current = filter(current,11, 2) # Using Savitzky-Golay filter
peakCurrent = peakdetect(current, excitationVoltage,10) # Detecting peak current

mass = (1/0.000001)*((peakCurrent-0.00000011)/0.0005)*0.02*298.374

# Displaying result
mass_string = str(round(mass))

lcd.message('  MASS IS \n   ' + mass_string) 

