#Crash Script, is meant to run if receiptPrint.py stops running for any reason

#!/usr/bin/python

from Adafruit_Thermal import *

if __name__  == "__main__":
        import sys
	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
	printer.setSize("L")
	printer.justify("C")
	printer.println("receiptPrint.py")
	printer.println(" has crashed.")
	printer.setSize("M")
	printer.println("Please power cycle the raspberry pi and the printer")
	printer.feed(1)
	printer.println("To do this unplug each plug for 10 seconds and then plug them")
	printer.println("back in")
	printer.feed(1)
	printer.println("If you continue to get this")
	printer.println("error, please contact")
	printer.println("Ryan Lehman @Cranbury Deliveries")
	printer.feed(3)
