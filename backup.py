#!/usr/bin/python

import sys, getopt
from google_drive import *
import datetime

class File:
	def __init__(self, name, path, isFolder, timestamp, size):
		self.name = name
		self.path = path
		self.isFolder = isFolder
		self.timestamp = timestamp
		self.size = size

def syncFolder(baseFolder, localFolderPath, remoteFolder, exclude, allowIncrease = True):
	print('Checking Folder: ' + localFolderPath)

	''' get local files '''
	localFiles = {}
	try:
		for localFileName in os.listdir(localFolderPath):
			localFilePath = os.path.join(localFolderPath, localFileName)
			include = True
			for e in exclude:
				if localFilePath.startswith(baseFolder + '\\' + e):
					include = False
			if include:
				try:
					localFiles[localFileName] = File(name = localFileName, path = localFilePath, isFolder = not os.path.isfile(localFilePath), timestamp = int(os.path.getmtime(localFilePath)), size = os.stat(localFilePath).st_size)
				except:
					print('Could not get info on file: ' + localFileName)
	except:
		print('Could not get info on directory: ' + localFolderPath)

	''' get remote files '''
	try:
		remoteFiles = remoteFolder.list()
	except:
		remoteFiles = {}

	''' remove any duplicate folders or files '''
	remoteFilesToTrash = []
	for remoteFileName in sorted(remoteFiles.keys()):
		remoteFile = remoteFiles[remoteFileName]
		if len(remoteFile.ids) > 1:
			print('Trashing Duplicate Files: ' + localFolderPath + '\\' + remoteFile.name)
			try:
				remoteFile.trashSelf()
				remoteFilesToTrash.append(remoteFile.name)
			except:
				print('Could not trash file: ' + localFolderPath + '\\' + remoteFile.name)
	for remoteFileName in remoteFilesToTrash:
		del remoteFiles[remoteFileName]

	remoteFilesToTrash = []
	''' remove any excess remote folders or files '''
	for remoteFileName in sorted(remoteFiles.keys()):
		remoteFile = remoteFiles[remoteFileName]
		if remoteFile.isFolder:
			if remoteFile.name not in localFiles:
				print('Trashing Folder: ' + localFolderPath + '\\' + remoteFile.name)
				try:
					remoteFile.trashSelf()
					remoteFilesToTrash.append(remoteFile.name)
				except:
					print('Could not trash folder: ' + localFolderPath + '\\' + remoteFile.name)
		else:
			if remoteFile.name not in localFiles:
				print('Trashing File: ' + localFolderPath + '\\' + remoteFile.name)
				try:
					remoteFile.trashSelf()
					remoteFilesToTrash.append(remoteFile.name)
				except:
					print('Could not trash file: ' + localFolderPath + '\\' + remoteFile.name)
	for remoteFileName in remoteFilesToTrash:
		del remoteFiles[remoteFileName]

	''' sync local files to remote files '''
	for localFileName in sorted(localFiles.keys()):
		localFile = localFiles[localFileName]
		if localFile.isFolder:
			if localFile.name not in remoteFiles:
				if allowIncrease:
					print('Creating Folder: ' + localFile.path)
					try:
						remoteFiles[localFile.name] = remoteFolder.createFolder(localFile.name)
					except:
						print('Could not create folder: ' + localFile.path)
		else:
			if localFile.name not in remoteFiles:
				if allowIncrease:
					print('Creating File: ' + localFile.path)
					try:
						remoteFolder.createFile(localFile.path, localFile.name, localFile.timestamp)
					except:
						print('Could not create file: ' + localFile.path)
			else:
				if localFile.timestamp != remoteFiles[localFile.name].timestamp:
					if allowIncrease or localFile.size >= remoteFiles[localFile.name].size:
						oldTime = datetime.datetime.fromtimestamp(remoteFiles[localFile.name].timestamp).strftime('%Y-%m-%d %H:%M:%S')
						newTime = datetime.datetime.fromtimestamp(localFile.timestamp).strftime('%Y-%m-%d %H:%M:%S')
						print('Updating File: ' + localFile.path + ' (' + oldTime + ' -> ' + newTime + ')')
						try:
							remoteFolder.updateFile(localFile.path, remoteFiles[localFile.name], localFile.timestamp)
						except:
							print('Could not update file: ' + localFile.path)

	''' recurse into sub folders '''
	for localFileName in sorted(localFiles.keys()):
		localFile = localFiles[localFileName]
		if localFile.isFolder and localFile.name in remoteFiles:
			syncFolder(baseFolder, localFile.path, remoteFiles[localFile.name], exclude, allowIncrease)

if __name__ == '__main__':
	help = 'See README.md for information. Syntax: backup.py -l <local folder> -d <drive folder> [-e <exclude folder>]* [--no-increase]'
	baseFolder = ''
	localFolder = ''
	driveFolder = ''
	allowIncrease = True
	exclude = []
	try:
		opts, args = getopt.getopt(sys.argv[1:],'hl:d:e:',['help', 'local-folder=', 'drive-folder=', 'exclude=', 'no-increase'])
	except getopt.GetoptError:
		print(help)
		sys.exit(-1)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print(help)
			sys.exit()
		elif opt in ("-l", "--local-folder"):
			localFolder = arg
			baseFolder = localFolder
		elif opt in ("-d", "--drive-folder"):
			driveFolder = arg
		elif opt in ("-e", "--exclude"):
			exclude.append(arg)
		elif opt == '--no-increase':
			allowIncrease = False
	if localFolder == '' or driveFolder == '':
		print(help)
		sys.exit(-1)
	googleDrive = GoogleDrive()
	remoteFolder = googleDrive.root().getAndCreateFolderPath(driveFolder)
	syncFolder(baseFolder, localFolder, remoteFolder, exclude, allowIncrease)
	
	# write timestamp file
	localFilePath = localFolder + '\\last_backup.txt'
	localTime = datetime.datetime.now()
	with open(localFilePath, 'a') as f:
		f.write(str(localTime) + '\n')
	remoteFolder.createFile(localFilePath, 'last_backup.txt', int(os.path.getmtime(localFilePath)))
	input('Press ENTER to exit')