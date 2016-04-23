
from __future__ import print_function 
import httplib2 
import os
import time
import base64
import email
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'ReceiptApp'

"""Gets and checks the credentials. DON'T FUCK WITH"""
def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

"""Get a list of Messages unread messages from mailbox from certain sender"""
def ListMessagesMatchingQuery(service, user_id, query):
	try:
		response = service.users().messages().list(userId=user_id,labelIds = 'UNREAD',q=query).execute() #Finds first result from query that is unread
		if response['resultSizeEstimate']!=0: #Makes sure there are some emails that are unread from query, if not it returns -1
			messages = response['messages']
			return messages
		else:
			return -1
	except errors.HttpError, error:
		print('An error occurred: %s' % error)

"""Checks f the message subject matches the restaurant ID"""
def isCorrectSubject(service,user_id,restaurant_id,message):
	foundMsg = service.users().messages().get(userId=user_id, id=message['id']).execute()
	headers = foundMsg['payload']['headers']
	subject = 'ERROR: UNABLE TO FIND SUBJECT'

	for header in headers: #looks for the subject key in the headers array and sets the subject value
		if header['name']=='Subject':
			subject = header['value']
	if subject == restaurant_id:
		print('Email Subject: '+subject)
		return True
	else:
		print('Looking for subject \''+restaurant_id+'\'. Found \''+subject+'\'.')
		print()
		return False

"""Prints out the messages and sets marks it as read"""
def PrintMessage(service,user_id,message):
	foundMsg = service.users().messages().get(userId=user_id, id=message['id']).execute()
	parts = foundMsg['payload']['parts']
	data = 'ERROR: UNABLE TO FIND DATA'
	for part in parts: #looks for the text/plain data key in the headers array and sets the data value
		if part['mimeType']=='text/plain':
			data = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')) #decodes the data from an encoded format to plain text

	service.users().messages().modify(userId = user_id,id=message['id'],body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute() #This marks email as read
	print('Email Data: '+data)

def main():
	sleepTime = 15 #CHANGE ME FOR HOW LONG TO WAIT INBETWEEN CHECKING EMAILS
	restaurant_id = 'Test 2' #CHANGE ME TO SPECIFIC RESTAURANT ID SO IT WILL MATCH SUBJECT
	emailToCheckFrom = 'from:aaronolkin@gmail.com' #CHANGE ME TO SENDER EMAIL
	user_id = 'me'

	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('gmail', 'v1', http=http)
	while True:
		messages = ListMessagesMatchingQuery(service,user_id,emailToCheckFrom) #Finds all emails from the email above that are also unread, returns as -1 if there are no unread messages from sender
		if messages !=-1:
			for message in messages:
				if isCorrectSubject(service,user_id,restaurant_id,message): #Makes sure the subject location matches the restaurant_id
					PrintMessage(service,user_id,message) #the print message function, printer API will be called in here with the subject and data recieved
		print('All emails have been checked '+emailToCheckFrom)
		print()
		time.sleep(sleepTime) #sleeps for certain amount of seconds in between checking
    
if __name__ == '__main__':
	main()