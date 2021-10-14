#import modules
import RPi.GPIO as GPIO
import time
import numpy as np
import matplotlib.pyplot as plt

#constant variables
leds = [21, 20, 16, 12, 7, 8, 25, 23]
dac = [26, 19, 13, 6, 5, 11, 9, 10]
comparator = 4
troykaVoltage = 17
bits = len(dac)
levels = 2 ** bits
dV = 3.3 / levels

#setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(leds + dac, GPIO.OUT)
GPIO.setup(troykaVoltage, GPIO.OUT)
GPIO.setup(comparator, GPIO.IN)

#functions for script
def num2pins(pins, value):
    GPIO.output(pins, [int(i) for i in bin(value)[2:].zfill(bits)])

def adc():

    value = 0
    up = True

    for i in range(bits):
        delta = 2 ** (bits - 1 - i)
        value = value + delta * (1 if up else -1)

        num2pins(dac, value)
        time.sleep(0.0011)

        up = bool(GPIO.input(comparator))

    return value

def adc3():
    mass = [0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(8):
        mass[i] = 1
        GPIO.output(dac, mass)
        time.sleep(0.001)

        if GPIO.input(comparator) == 0:
            mass[i] = 0  

    return mass[0]*(2**7) + mass[1]*(2**6) + mass[2]*(2**5) + mass[3]*(2**4) + mass[4]*(2**3) + mass[5]*(2**2) + mass[6]*(2**1) + mass[7]*(2**0)

#main logic of the script
try:
    #create variables
    measure = [] #create mass
    value = 0

    #fixed start time
    start = time.time()
    
    #cange capacitor
    GPIO.output(troykaVoltage, 1)
    
    while value <= 235:
        value = adc3()
        num2pins(leds, value)
        measure.append(value)
        print("Capacitor is charging: {:.2f}".format(value))

    #discharge capacitor
    GPIO.output(troykaVoltage, 0)
   
    while value > 1:
        value = adc3()
        num2pins(leds, value)
        measure.append(value)
        print("Capacitor is discharging")

    #fix finish time and print time values
    finish = time.time()

    totalTime = finish - start
    measurePeriod = totalTime / len(measure)
    samplingFrequency = int(1 / measurePeriod)

    print("Total measure time: {:.2f} s, measure period: {:.3f} ms, sampling frequency: {:d} Hz".format(totalTime, measurePeriod, samplingFrequency))
    print("Voltage step: {:.3f} V".format(dV))

    #plot results
    plt.plot(measure)
    plt.show()
    np.savetxt('/home/gr101/Desktop/Scripts/settings.txt', dV, fmt='%d')
    np.savetxt('/home/gr101/Desktop/Scripts/data.txt', measure, fmt='%d')

finally:
    GPIO.cleanup()
    print('GPIO cleanup completed.')