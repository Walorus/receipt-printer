#!/usr/bin/python

from Adafruit_Thermal import *
WHERE = "Teddy's"
lineLength=24
URL = "https://app.cranburydeliveries.com/retrieve/{}/"
URL = "http://app.cranburydeliveries.com:8080/retrieve/{}/" # For testing
from urllib2 import urlopen
from urllib2 import HTTPError
from json import loads

def main(orderDictionary): #almost all of the following is just formatting
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
		finalLine = breakIntoLines(item['name'],False,printer)
		printer.printNoLine(finalLine)
		for i in range(0,lineLength-len(finalLine)):
                                printer.printNoLine(".")
		printer.printNoLine(" $")
		printer.println('{0:.2f}'.format(item['price']))
		printer.setSize("S")
		printer.setLineHeightSmall()
		for addon in item['addons']:
			finalAddonLine = breakIntoLines(addon['name'],True,printer)
                        printer.printNoLine("  "+finalAddonLine)
			for i in range(0,lineLength-len(finalAddonLine)-2):
                       		printer.printNoLine(".")
			printer.printNoLine(" $")
			printer.println('{0:.2f}'.format(addon['price']))
			printer.println()
		
		if item['comments']:
			printer.printNoLine("  (")
                        finalCommentLine = breakIntoLines(item['comments'],True,printer)
                        printer.printNoLine(finalCommentLine)
			printer.println(")")

		else:
			printer.println("  (No comments)")
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
	printer.setLineHeight(32)
	printer.feed(8)
	
	#printer.setDefault() # Restore printer to defaults

def breakIntoLines(currentLine,addSpaces,printer): #breaks lines greater than the lineLength set at top into properly sized lines
	#If any words are > lineLength makes them less than lineLength
	tempLineLength = lineLength
	if addSpaces:
		tempLineLength-=2
	words = currentLine.split()
	for i in range(0,len(words)):
		if len(words[i])>tempLineLength:
			words[i]=words[i][:tempLineLength]
	lastLine = ' '.join(words)
	if len(currentLine)>=tempLineLength:	#if the whole line is greater, removes words until it isn't
		firstLine = ' '.join(currentLine.split()[:len(currentLine.split())-1])
		arrayLength = len(currentLine.split())
		wordsRemoved = 1
		while(len(firstLine)>tempLineLength+5):
			firstLine = ' '.join(firstLine.split()[:len(firstLine.split())-1])
			wordsRemoved+=1
		lastLine=' '.join(currentLine.split()[arrayLength-wordsRemoved:])
		if addSpaces:
			printer.printNoLine("  ")
		printer.println(firstLine)
		if len(lastLine)>tempLineLength :
			lastLine = breakIntoLines(lastLine,addSpaces,printer) #if the remaining removed words are still greater, does it again recursively
	return lastLine

def get_one_order(where=WHERE): #Aaron's method to get the order dictionary object, returns false if no objects available
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
			print("No open orders currently") #Only seen in console, exists to show that it is running
			time.sleep(25)
		time.sleep(5)
#	order = {'number':101,'cost':25,'tax':1.02,'driver':5.00,'total':30,'items':[{'name':"Burger",'price':10.50,'comments':"No tomato",
#		'addons':[{'name':"Cheddar Cheese",'price':4.0},{'name':"Bacon",'price':2.0}]},
#                {'name':"Hotdog Surprise",'price':8.50,'comments':"No mustard",'addons':[]}]}
#	main(order)
#Above used for testing and formatting, a hardcoded order
