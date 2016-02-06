# google-drive-backup
A one-way backup of local folders onto your Google Drive

## Installation
1. Copy/clone this repository into a folder on your device.
2. If you don't have Python 3, download and install it (https://www.python.org/downloads/)
3. Setup the Python modules:
  - On Mac
    1. `pip install --upgrade pip`
    2. `pip install --upgrade google-api-python-client`
  - On Windows:
  - 1. `reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_SZ /d "%path%;c:\python2.7"`
    1. `python -m pip install --upgrade pip`
    2. `python -m pip install --upgrade google-api-python-client`
4. Setup the Google Drive API
  1. Go to https://console.developers.google.com
  2. Create a new project and give it a name.
  3. Use Google APIs -> Drive API -> Enable API
  4. Credentials -> New Credentials -> OAuth Client ID -> Configure Consent Screen
  5. Fill out the form -> Other -> Save the client secret for later
  6. On the far right, download to client_secret.json in your google-drive-backup folder.
5. `python backup.py <local folder> <drive folder>`
6. A browser window will open asking for your client secret that you saved from before. Enter it.
7. You're done!

## Syntax

`python backup.py -l <local folder> -d <drive folder> [--delete-only]`

- **\<local folder\>** The folder path that you would like backed up. It can be absolute or relative to the google-drive-backup folder.
- **\<drive folder\>** The folder path on your Google Drive that you want to store your backed up folder. If it doesn't exist, it will be created. It uses forward slashes as the folder separator.
- **\[no-increase\]** If the phrase "no-increase" is used, there will be no new folders or files created, and only files that are a smaller size than the drive version will be uploaded. This is useful for when you need to run delete before adding more files becuase of the Google Drive size limit.