# ERPNext Remote Backup Script

This script will allow you to backup your ERPNext instance in two steps:
1. You configure a backup-restore.json file with your server IP, credentials and your local machine's SSH keys
2. You run the script

The json file must be located one directory above the script: `erpnext-backup.py`
## Requirements
* Python 3.6
* Your local machine MUST have a SSH private key registered, so that it may open the remote server 
previously configured with the private keys complementary public key. [Here](https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/to-account/) 
are some references on using SSH keys. Just remember: Register your private key on the local machine, and
add the public key on the remote server where you will be backing up and the remote server where you will be restoring.

## Configuration

Using a text editor, open the generic `backup-restore.json` file located in this directory
Change the key values appropriately
Save in the parent directory where you cloned this GitHub repository.
(This is for security reasons, in case you edit this on your fork, you would not want to push a file with all your credentials, right?)

`hostname`: The server address of your ERPNext instance.  For example: `192.168.1.38`
`user`: The username configured on your server instance when setting up your server. For example: `james`
`password`: The password you use when logging in to your server instance. 
Usually when you don't have an ssh key configured, this is used. It can be left blank if using ssh key authentication
`mySSHK`: Your public key file with complete path. For example: `/Users/myuser/.ssh/my-key-name.pub`
`mySSHK_passphrase`: The passphrase you entered to access you private key when generating your key pair.
our public key file with complete path. This is the passphrase that you entered when you ran `ssh-keygen` . 
This passphrase keeys the private key encrypted, and adds extra security.
`sites`: An array of site names on the server.  Currently it is not being used.  Planned for further support of multiple site backups.

`backup_dir`: The directory in the remote server where the backup will be written. I recommend `home`

`backup_filename`: The filename which will be used when constructing the complete filename for the database backup.  
This script will create a new `.sql` file whose name equals the `hostname-year-month-day-hour-minute-backup-filename.sql`

`pvt_files_backup_filename`: The filename which will be user when constructing the complete filename for the private files backup.
This script will create a new `.gz` file whose name will be `hostname-year-month-day-hour-minute-pvt_files_backup_filename.tar.gz`

`pub_files_backup_filename`: The filename which will be user when constructing the complete filename for the public files backup.
This script will create a new `.gz` file whose name will be `hostname-year-month-day-hour-minute-pub_files_backup_filename.tar.gz`
## Usage:

`python3.6 erpnext-backup.py`