from __future__ import print_function
import httplib2
import argparse
import os
import time
import calendar

from datetime import datetime

from apiclient import discovery
from apiclient.http import MediaFileUpload

import oauth2client
from oauth2client import client
from oauth2client import tools

import pprint

''' https://console.developers.google.com/project to set things up '''

class GoogleDrive:
	SCOPES = 'https://www.googleapis.com/auth/drive'
	CLIENT_SECRET_FILE = 'client_secret.json'
	APPLICATION_NAME = 'Google Drive API'

	class File:
		''' returns the child file of the given name in the folder, or None of the file does not exist '''
		def child(self, name):
			results = self.service.files().list(q = '\'' + self.id + '\' in parents and title = \'' + name + '\'').execute()
			items = results.get('items', [])
			if items:
				for item in items:
					if item['labels']['trashed']:
						continue
					return self.getFileFromItem(item)
			return None

		''' returns dictionary of files and folders in a given folder '''
		def list(self):
			pageToken = None
			files = {}
			while True:
				results = self.service.files().list(q = '\'' + self.id + '\' in parents', orderBy = 'title', pageToken = pageToken).execute()
				items = results.get('items', [])
				if items:
					for item in items:
						if item['labels']['trashed']:
							continue
						file = self.getFileFromItem(item)
						if file.name in files:
							files[file.name].ids.append(file.id)
						else:
							files[file.name] = file
				pageToken = results.get('nextPageToken')
				if not pageToken:
					break
			return files

		''' creates a new folder as a child '''
		def createFolder(self, name):
			body = {
				'parents': [{'id': self.id}],
				'title': name,
				'mimeType': 'application/vnd.google-apps.folder'
			}
			item = self.service.files().insert(body = body).execute()
			return self.getFileFromItem(item)

		''' uploads a new file as a child from the given localFilePath and localFileName '''
		def createFile(self, localFilePath, localFileName, timestamp):
			body = {
				'parents': [{'id': self.id}],
				'title': localFileName,
				'modifiedDate': datetime.utcfromtimestamp(timestamp).isoformat() + '.000Z'
			}
			if os.stat(localFilePath).st_size > 0:
				media_body = MediaFileUpload(localFilePath, resumable = True)
				if media_body.mimetype() is None:
					media_body = MediaFileUpload(localFilePath, mimetype = '*/*', resumable = True)
				request = self.service.files().insert(body = body, media_body = media_body)
				response = None
				while response is None:
					status, response = request.next_chunk()
			else:
				response = self.service.files().insert(body = body).execute()
			return self.getFileFromItem(response)

		def trashSelf(self):
			for id in self.ids:
				self.service.files().trash(fileId = id).execute()
			
		''' updates a child file from the given localFilePath and localFileName '''
		def updateFile(self, localFilePath, remoteFile, timestamp):
			body = {
				'parents': [{'id': self.id}],
				'title': remoteFile.name,
				'modifiedDate': datetime.utcfromtimestamp(timestamp).isoformat() + '.000Z'
			}
			media_body = MediaFileUpload(localFilePath, resumable = True)
			if media_body.mimetype() is None:
				media_body = MediaFileUpload(localFilePath, mimetype = '*/*', resumable = True)
			request = self.service.files().update(fileId = remoteFile.id, body = body, media_body = media_body, setModifiedDate = True)
			response = None
			while response is None:
				status, response = request.next_chunk()
			item = response
			return self.getFileFromItem(item)

		def __init__(self, service, id, name, isFolder, timestamp, size):
			self.service = service
			self.id = id
			self.name = name
			self.isFolder = isFolder
			self.timestamp = timestamp
			self.size = size
			self.ids = [id]

		def getFileFromItem(self, item):
			suffix = ''
			if item['mimeType'] == 'application/vnd.google-apps.document':
				suffix = '.gdoc'
			elif item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
				suffix = '.gsheet'
			return GoogleDrive.File(service = self.service, id = item['id'], name = item['title'] + suffix, isFolder = (item['mimeType'] == 'application/vnd.google-apps.folder'), timestamp = int(calendar.timegm(time.strptime(item['modifiedDate'] + '0', '%Y-%m-%dT%H:%M:%S.%fZ0'))), size = int(item['fileSize']) if ('fileSize' in item) else 0)

	''' returns the root folder '''
	def root(self):
		return GoogleDrive.File(self.service, 'root', '', True, '0', 0)

	def __init__(self):
		store = oauth2client.file.Storage('./credentials.json')
		credentials = store.get()
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(GoogleDrive.CLIENT_SECRET_FILE, GoogleDrive.SCOPES)
			flow.user_agent = GoogleDrive.APPLICATION_NAME
			parser = argparse.ArgumentParser(parents=[tools.argparser])
			flags = parser.parse_args()
			credentials = tools.run_flow(flow, store, flags = flags)
		self.credentials = credentials
		self.http = credentials.authorize(httplib2.Http())
		self.service = discovery.build('drive', 'v2', http=self.http)

