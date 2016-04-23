#!/usr/bin/python

from Adafruit_Thermal import *
WHERE = "Teddy's"
lineLength=24
URL = "https://app.cranburydeliveries.com/retrieve/{}/"
URL = "http://app.cranburydeliveries.com:8080/retrieve/{}/" # For testing
from urllib2 import urlopen
from urllib2 import HTTPError
from json import loads

def main(orderDictionary):
	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
	dict = orderDictionary
	printer.setLineHeightSmall()
	printer.justify("C")
	printer.boldOn()
	printer.setSize("L")
	printer.println(WHERE)
	printer.setSize("M")
	printer.printNoLine("Order ")
	printer.println(dict['number'])
	printer.boldOff()
	printer.justify("L")
	printer.setSize("M")
	for item in dict['items']:
		printer.setSize("M")
		printer.justify("L")
		finalLine=item['name']
		if len(finalLine) < lineLength:
			printer.printNoLine(finalLine)
		else:
			words = finalLine.split()
			for i in range(0,len(words)):
				if len(words[i])>24:
					words[i]=words[i][:24]
			finalLine = breakIntoNewLine(' '.join(words),printer)
			printer.printNoLine(finalLine)
		for i in range(0,lineLength-len(finalLine)):
                                printer.printNoLine(".")
		printer.printNoLine(" $")
		printer.println('{0:.2f}'.format(item['price']))
		printer.setSize("S")
		printer.setLineHeightSmall()
		for addon in item['addons']:
                        printer.printNoLine(addon['name'])
			for i in range(0,lineLength-len(addon['name'])):
                       		printer.printNoLine(".")
			printer.printNoLine(" $")
			printer.println('{0:.2f}'.format(addon['price']))
		printer.println("("+item['comments']+")")
	printer.setSize("M")
	printer.println("Delivery Fee............ $5.00")
	printer.println("______________________________")
	printer.println()
	printer.println()
	printer.printNoLine("Total")
	for i in range(0,lineLength-len("Total")):
		printer.printNoLine(".")
	printer.printNoLine(" $")
	printer.println('{0:.2f}'.format(dict['cost']+dict['driver']))
	printer.setLineHeight(24)
	printer.feed(3)
	
	#printer.setDefault() # Restore printer to defaults

def breakIntoNewLine(currentLine,printer):
	firstLine = ' '.join(currentLine.split()[:len(currentLine.split())-1])
	arrayLength = len(currentLine.split())
	wordsRemoved = 1
	while(len(firstLine)>lineLength+5):
		firstLine = ' '.join(firstLine.split()[:len(firstLine.split())-1])
		wordsRemoved+=1
	lastLine=' '.join(currentLine.split()[arrayLength-wordsRemoved:])
	printer.println(firstLine)
	if len(lastLine)>lineLength :
		lastLine = breakIntoNewLine(lastLine,printer)
	return lastLine

def get_one_order(where=WHERE):
    try:
        fd = urlopen(URL.format(where))
        text = fd.read().decode()
        obj = loads(text)
        return obj
    except HTTPError as err:
        if err.code == 404:
            return None
        else:
            return False

if __name__  == "__main__":
	import sys,time
	while(True):
		orderReturn = get_one_order()
		if orderReturn:
			main(orderReturn)
		else:
			print("Sorry no orders")
		time.sleep(30)
#	order = {'number':101,'cost':25,'tax':1.02,'driver':5.00,'total':30,'items':[{'name':"Burger",'price':10.50,'comments':"No tomato",
#		'addons':[{'name':"Cheddar Cheese",'price':4.0},{'name':"Bacon",'price':2.0}]},
#                {'name':"Hotdog Surprise",'price':8.50,'comments':"No mustard",'addons':[]}]}
#	main(order)
#Above used for testing and formatting, a hardcoded order
