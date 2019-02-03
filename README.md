# ERPNext Remote Backup Script

This script will allow you to backup your ERPNext instance in two steps:
1. You configure a backup-restore.json file with your server IP, credentials and your local machine's SSH keys
2. You run the script

The json file must be located one directory above the script: `erpnext-backup.py`
## Requirements
* Python 3.6
* Your local machine MUST have SSH private key registered, so that it may open the remote server previously configured with its complementary public key
* 
## Configuration

Using a text editor, open the generic `backup-restore.json` file located in this directory
Change the key values appropriately
Save in the parent directory where you cloned this GitHub repository.
(This is for security reasons, in case you edit this on your fork, you would not want to push a file with all your credentials, right?)


## Usage:

`python3.6 erpnext-backup.py`