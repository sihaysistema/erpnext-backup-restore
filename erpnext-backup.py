#!/usr/bin/python3.6
import sys
import os
import paramiko
import time
import datetime
import json
from commands import commands_array
from commands import commands_dict
from os import path
from pathlib import Path
from inspect import currentframe, getframeinfo
import ftputil
import subprocess
from scp import scp_remote_to_local, scp_local_to_remote

server_json = 'backup-restore.json'
filename = getframeinfo(currentframe()).filename
onedirup = Path(filename).resolve().parent.parent

nl = '\n'
fwd = '/'
title = 'ERPNext Server Backup Utility'
json_read = 'Reading JSON file...'
header1 = '==========================='
spc = ' '
sql = '.sql'
dash = '-'
tar = 'tar'
dot = '.'
gz = 'gz'
one_stb = 'Server to backup'
many_stb = one_stb.replace('Server', 'Servers')
password = ''
executing = 'Executing: '
mysql_pass = ''
mysql_dump = 'mysqldump -u root -p'
tar_cmd = 'tar cvzf'
bench_dir = 'frappe/frappe-bench'
sites = '/sites'

# This function opens up the json located on directory above the script.
# it only runs once to load all the contents as json objects.
def read_json():
    """This function reads the json and returns the entire contents as a dictionary"""
    print(header1 + spc + json_read + spc + header1)
    with open((os.path.join(onedirup, server_json))) as backup_restore_file:
        backup_restore_data = json.load(backup_restore_file)
    json_read_result = 'JSON has been read properly...'
    print(json_read_result)
    return backup_restore_data

def get_backup_servers():
    """This function gets the array of servers to be backed up"""
    # gets the entire json
    json = read_json()
    # print(json)
    backup_servers = json['ERPNext_servers_to_backup'] 
    # print(backup_servers)   
    return backup_servers

def get_local_machine_data():
    """This function gets the json data of locla machine data like download folder, sudo password, etc. Returns a dictionary"""
    # gets the entire json
    json = read_json()
    # print(json)
    local_machine_data = servers_list['Local_machine_data'] 
    # print(backup_servers)   
    return local_machine_data

def read_server_json():
    """This reads the JSON file and assigns the contents to dictionaries and arrays, which will be globally accessible"""
    with open((os.path.join(onedirup, server_json))) as backup_restore_file:
        # print('file opened')
        global backup_restore_data
        global backup_servers
        global server_data
        global restore_servers
        global local_machine_data
        backup_restore_data = json.load(backup_restore_file)
        backup_servers = backup_restore_data['ERPNext_servers_to_backup']
        # this will be switched off until a proper solution for server restoration is created.  Restore servers will take local files and execute a restore as per the json configuration.
        restore_servers = backup_restore_data['ERPNext-servers_to_restore']
        # print(str(local_dir1))
        print(header1 + spc + json_read + spc + header1)
        json_read_result = 'JSON has been read properly...'
    # HOW DO I RETURN THE VALUES OF THESE VARIABLES FOR USE ELSEWHERE? FIXME TODO
    return backup_servers

# def upload_files(local_file_path):
#     """This function will upload files to a remote server"""
#     global remote_dir
#     remote_dir = server_data['restore_copy_dir']
#     # temporarily, we assume the home directory exists in the remote linux server
#     print('Will be uploading this file: ' + local_file_path)  #WIP WIP WIP FIXME TODO
#     scp_local_to_remote(hostname, user, remote_path, local_path_and_filename)
#     else:
#         print('Directory exists, using existing directory: ' + str(local_dir))
#         print('Will be downloading this file: ' + remote_file_path)
#         scp_local_to_remote(hostname, user, remote_path, local_path_and_filename)

def download_files(remote_file_path):
    """This function will download files from a remote server. It checks for the existence of
    the local directory, based on data passed in backup-restore.json. It then calls the scp_remote_to_local
    from the scp module to execute the scp command."""  #FIXME:  This function should receive the 4 arguments of hostname, user, remote_file_path and local_dir
    global local_dir
    local_dir = local_machine_data['local_download_directory']
    if not os.path.exists(local_dir):
        os.mkdir (local_dir)
        print('Local path does not exist, creating the directory:' + str(local_dir))
        print('Will be downloading this file: ' + remote_file_path)
        scp_remote_to_local(hostname, user, remote_file_path, local_dir)
    else:
        print('Directory exists, using existing directory: ' + str(local_dir))
        print('Will be downloading this file: ' + remote_file_path)
        scp_remote_to_local(hostname, user, remote_file_path, local_dir)

def sql_db_backup_cmd(remote_backup_dir, hostname, time, filename, mysql_pass, db_name):
    """This function concatenates remote file path and filename to be used when constructing the command to execute a mysqldump backup
    It also creates the command and returns it ready to be executed"""
    remote_db_dl_file_path = str(remote_backup_dir) + fwd + str(hostname).replace(".", "_") + dash + time.strftime('%Y-%m-%d-%H-%M') + dash + str(filename) + sql
    # print(str(remote_db_dl_file_path))
    # Concatenate the command string for backing up the database
    sql_db_backup_cmd = mysql_dump + mysql_pass + spc + str(db_name) + spc + '> ' + str(remote_db_dl_file_path)
    # print(str(sql_db_backup_cmd))
    return sql_db_backup_cmd

def files_backup_cmd(remote_backup_dir, hostname, time, filename, tar_args, sitename):
    """This function concatenates remote file path and filename to be used when constructing the command to execute a tar
    compression for the site folder for that server.
    It also creates the command and returns it ready to be executed"""
    
    # Concatenate the command string for backing up the site folder
    remote_site_dl_file_path = str(remote_backup_dir) + fwd + str(hostname).replace(".", "_")) + dash + time.strftime('%Y-%m-%d-%H-%M') + dash + str(filename) + dot + tar + dot + gz
    # print(str(remote_pvt_dl_file_path))
    site_file_backup_cmd = tar + spc + tar_args + spc + str(remote_site_dl_file_path) + spc + str(remote_backup_dir) + fwd + bench_dir + sites + fwd + str(sitename)
    # print(str(site_file_backup_cmd))
    return site_file_backup_cmd

def run_server_backups(backup_servers, time):
    """Runs the server backups.
    1. It will iterate through the amount of servers passed in the JSON
    2. It opens an ssh connection with Paramiko to execute commands
    3. Once open, it tries getting the db password from the passwords.txt file that ERPNext creates during setup.
    4. It concatenates the command string for backing up the database to be sent
    5. It sends the database backup command and waits for a response
    6. It concatenates the command string for backing up the sites folder to be sent
    7. It sends the tar compress command and waits for a response
    8. It then downloads the database and the tar.gz file created, to the local directory specified
    9. If the restore server data is passed, including a copy_files_to_remote: true  key in the json, it will copy the files
    10. If the execute_restore: true key is passed in the backup-restore.json, then the files will be placed in their directories,
     and the database restored
    """
    server_count = 1
    prog_status = ''
    try:
        prog_status = 'Iterating through servers...'
        for p in backup_servers:
            # enumerating the index of backup_servers
            index, item = next(enumerate(backup_servers))
            # Testing enumeration, since i cannot use "p"
            # hostname = backup_servers[index]['hostname']
            hostname = p['hostname']
            user = p['user']
            mySSHK_passphrase = p['mySSHK_passphrase']
            print(backup_servers[index]['hostname'])
            print('***** Server #' + str(server_count) + ' *****')
            print('Hostname: ' + p['hostname'] + nl + 'User: ' + p['user'])
    
            # Open the SSH connection
            ssh = paramiko.SSHClient() # Creates an SSHClient object instance to connect with
            # Add the locally available SSH Keys to the ssh connection object.
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())# no known_hosts error
            # ssh.load_system_host_keys()
            # Connect
            ssh.connect(hostname, username=user, passphrase=mySSHK_passphrase) #no password needed           ssh.connect(hostname, username=user, passphrase=password, password=password) # When using password only use this
            prog_status = 'Successfully connected to %s' % hostname
            print(str(prog_status))

            # Obtain database user and password
            # Access the content of a remote file containing JSON data.
            # We obtain the password for the database file
            try:
                prog_status = 'Getting data from passwords.txt...'
                print(str(prog_status))
                sftp_client = ssh.open_sftp()
                remote_file = sftp_client.open(commands_dict['passwords_file'])
                json_data = json.load(remote_file)
                # print(str(json_data))
                mysql_pass = json_data['mysql_root_password']
                # print(mysql_pass)
                remote_file.close()
                prog_status = 'Database password successfully obtained...' #+ str(mysql_pass)
                print(str(prog_status))
            except:
                prog_status = "Error obtaining database user and password"
                remote_file.close()
            
            # Create the backup command to be executed for backing up the remote db.
            cmd1 = sql_db_backup_cmd(backup_servers[index]['backup_dir'],backup_servers[index]['hostname'], time, backup_servers[index]['sql_backup_filename'], mysql_pass, commands_dict['db_name'])
            # print(cmd1)
            
            
           

            # We now backup the database
            prog_status = 'Begin Database back up...'
            print(str(prog_status))
            stdin, stdout, stderr = ssh.exec_command(sql_db_backup_cmd)
            channel = stdout.channel
            status = channel.recv_exit_status()
            if status == 0:
                for line in stdout.read().splitlines():
                    result = str(line, 'utf-8')
                prog_status = 'SQL Database successfully backed up.'
                print(str(prog_status))
            else:
                prog_status = 'No Backups made'
                # print(str(prog_status))

            # We now backup the site folder
            prog_status = 'Begin File back up...'
            print(str(prog_status))
            stdin, stdout, stderr = ssh.exec_command(site_file_backup_cmd)
            channel = stdout.channel
            status = channel.recv_exit_status()
            if status == 0:
                for line in stdout.read().splitlines():
                    result = str(line, 'utf-8')
                for line in stderr.read().splitlines():
                    result = str(line, 'utf-8')
                prog_status = 'Site folder successfully backed up.'
                # print(str(prog_status))
            else:
                for line in stdout.read().splitlines():
                    result = str(line, 'utf-8')
                for line in stderr.read().splitlines():
                    result = str(line, 'utf-8')
                prog_status = 'No Sites folder file backups were made'
                # print(str(prog_status))
            ssh.close()
            server_count += 1

            # We now download the database we just backed up here
            # WORKS OK
            # download_files(remote_db_dl_file_path)
            # WORKS OK

            # And the private + public files
            # WORKS OK
            # download_files(remote_site_dl_file_path)
            # WORKS OK

            # Check if user wants to restore files, either True or False
            # print('Contents of: ' + str(server_data['execute_restore']))
            # if server_data['copy_files_to_remote'] is not False:
#                 print('do copy the files')
#                 # We upload the database to the server to be restored
#                 remote_db_ul_file_path = server_data['restore_copy_dir']
#
#                 print(str(remote_db_ul_file_path))
#                 # scp_local_to_remote(hostname, user, remote_path, local_path_and_filename):
#                 # upload_files(remote_db_ul_file_path)
#
#                 # We upload the sites folder to the server to be restored
#                 # upload_db(remote_db_ul_file_path)
#
#                 # Check if user wants to restore files, either True or False
#                 # print('Contents of: ' + str(server_data['execute_restore']))
#                 if server_data['execute_restore'] is not False:
#                     print('do the restore')
#                 else:
#                     print('no restore requested')
#             else:
#                 print('no file copy requested, ignoring restore flag, whichever it may be')
    except:
        prog_status = 'Oops!, something in the backup routine failed! check run_server_backups() function or data passed to it!'
    return prog_status

def clean_up():
    """This functions cleans up the locally downloaded files.  This"""
    pass

def run_all():
    """Main program running function. it:
    1. Prints a title to the terminal showing program has been initiated
    2. Calls the read_server_json() function to read the json file with backup and restore server configuration
    3. Sets up"""
    print(header1 + spc + title + spc + header1)
    # RUN Everything
    try:
        begin_time = datetime.datetime.now()    
        backup_servers = get_backup_servers()
        # Will read how many servers must be backed up
        if len(backup_servers) == 1:
            print(header1 + spc + str(len(backup_servers)) + spc + one_stb + spc + header1)
        else:
            print(header1 + spc + str(len(backup_servers)) + spc + many_stb + spc + header1)
        print(str(run_server_backups(backup_servers, begin_time)))
        #run server_restores
    except:
        end_time = datetime.datetime.now()
        print('The process took: ' + str((end_time - begin_time)))
        print('Something failed, could not execute remote server database backup. Check individual functions, json file  for answers.')
    finally:
        end_time = datetime.datetime.now()
        print('The process took: ' + str((end_time - begin_time)))
        print('ERPNext Backup Process Completed')

run_all()
