
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


def get_credentials():
    """Gets valid user credentials from storage. DONT FUCK WITH.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
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

"""Get a list of Messages unread messages from mailbox from certain sender
"""

def ListMessagesMatchingQuery(service, user_id, query):
	try:
		response = service.users().messages().list(userId=user_id,labelIds = 'UNREAD',q=query,maxResults=1).execute() #Finds first result from query that is unread
		if response['resultSizeEstimate']!=0: #Makes sure there are some emails that are unread from query, if not it returns -1
			messages = response['messages']
			return messages[0]
		else:
			return -1
	except errors.HttpError, error:
		print('An error occurred: %s' % error)

"""Prints out the messages and sets marks it as read"""

def PrintMessages(service,user_id,message,restaurant_id):
	foundMsg = service.users().messages().get(userId=user_id, id=message['id']).execute()
	headers = foundMsg['payload']['headers']
	parts = foundMsg['payload']['parts']
	subject = 'ERROR: UNABLE TO FIND SUBJECT'
	data = 'ERROR: UNABLE TO FIND DATA'

	for header in headers: #looks for the subject key in the headers array and sets the subject value
		if header['name']=='Subject':
			subject = header['value']
	for part in parts: #looks for the text/plain data key in the headers array and sets the data value
		if part['mimeType']=='text/plain':
			data = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')) #decodes the data from an encoded format to plain text
	service.users().messages().modify(userId = user_id,id=message['id'],body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute() #This marks email as read

	if restaurant_id==subject:
		print('Email Subject: '+subject)
		print('Email Data: '+data)

def main():
	restaurant_id = 'Test 1' #Used to compare to subject line, subject line should have the specific restaurant_id
	emailToCheckFrom = 'from:aaronolkin@gmail.com' #CHANGE ME TO SENDER EMAIL
	user_id = 'me'
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('gmail', 'v1', http=http)
	while True:
		keepChecking = True
		while keepChecking:
			message = ListMessagesMatchingQuery(service,user_id,emailToCheckFrom) #Finds all emails from the email above that are also unread
			if message !=-1: 
				PrintMessages(service,user_id,message,restaurant_id) #the print message function, printer API will be called in here with the subject and data recieved
			else: #if -1 IS returned means there are no unread left to check, so it sleeps until function is called again
				print("No unread emails "+emailToCheckFrom) 
				keepChecking = False #If there are no more unread emails from the sender than it stops checking.
		time.sleep(15)
    


if __name__ == '__main__':
	main()