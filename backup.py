from google_drive import *

rootFolderPath = 'C:\\stephen\\drive_new'

class File:
	def __init__(self, name, path, isFolder, timestamp, size):
		self.name = name
		self.path = path
		self.isFolder = isFolder
		self.timestamp = timestamp
		self.size = size

def syncFolder(localFolderPath, remoteFolder, allowIncrease = True):
	print(localFolderPath)

	''' get local files '''
	localFiles = {}
	for localFileName in os.listdir(localFolderPath):
		localFilePath = os.path.join(localFolderPath, localFileName)
		localFiles[localFileName] = File(name = localFileName, path = localFilePath, isFolder = not os.path.isfile(localFilePath), timestamp = int(os.path.getmtime(localFilePath)), size = os.stat(localFilePath).st_size)

	''' get remote files '''
	remoteFiles = remoteFolder.list()
	
	''' remove any duplicate folders or files '''
	remoteFilesToTrash = []
	for remoteFileName in sorted(remoteFiles.keys()):
		remoteFile = remoteFiles[remoteFileName]
		if len(remoteFile.ids) > 1:
			print('Trashing Duplicate Files: ' + localFolderPath + '\\' + remoteFile.name)
			remoteFile.trashSelf()
			remoteFilesToTrash.append(remoteFile.name)
	for remoteFileName in remoteFilesToTrash:
		del remoteFiles[remoteFileName]

	remoteFilesToTrash = []
	''' remove any excess remote folders or files '''
	for remoteFileName in sorted(remoteFiles.keys()):
		remoteFile = remoteFiles[remoteFileName]
		if remoteFile.isFolder:
			if remoteFile.name not in localFiles:
				print('Trashing Folder: ' + localFolderPath + '\\' + remoteFile.name)
				remoteFile.trashSelf()
				remoteFilesToTrash.append(remoteFile.name)
		else:
			if remoteFile.name not in localFiles:
				print('Trashing File: ' + localFolderPath + '\\' + remoteFile.name)
				remoteFile.trashSelf()
				remoteFilesToTrash.append(remoteFile.name)
	for remoteFileName in remoteFilesToTrash:
		del remoteFiles[remoteFileName]

	''' sync local files to remote files '''
	for localFileName in sorted(localFiles.keys()):
		localFile = localFiles[localFileName]
		if localFile.isFolder:
			if localFile.name not in remoteFiles:
				if allowIncrease:
					print('Creating Folder: ' + localFile.path)
					remoteFiles[localFile.name] = remoteFolder.createFolder(localFile.name)
		else:
			if localFile.name not in remoteFiles:
				if allowIncrease:
					print('Creating File: ' + localFile.path)
					remoteFolder.createFile(localFile.path, localFile.name, localFile.timestamp)
			else:
				if localFile.timestamp != remoteFiles[localFile.name].timestamp:
					if allowIncrease or localFile.size >= remoteFiles[localFile.name].size:
						print('Updating File: ' + localFile.path + '(timestamp ' + str(localFile.timestamp) + '/' + str(remoteFiles[localFile.name].timestamp) + ')')
						remoteFolder.updateFile(localFile.path, remoteFiles[localFile.name], localFile.timestamp)

	''' recurse into sub folders '''
	for localFileName in sorted(localFiles.keys()):
		localFile = localFiles[localFileName]
		if localFile.isFolder and localFile.name in remoteFiles:
			syncFolder(localFile.path, remoteFiles[localFile.name], allowIncrease)

googleDrive = GoogleDrive()
# syncFolder(rootFolderPath, googleDrive.root().child('backup'), False) # only delete first
syncFolder(rootFolderPath, googleDrive.root().child('backup'))