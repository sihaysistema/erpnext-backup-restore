#!/usr/bin/python3.6
import sys
import os
import paramiko
import time
import json
from commands import commands_array
from commands import commands_dict
from os import path
from pathlib import Path
from inspect import currentframe, getframeinfo

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
one_stb = 'Server to backup'
many_stb = one_stb.replace('Server', 'Servers')
password = ''
executing = 'Executing: '
mysql_pass = ''
mysql_dump = 'mysqldump -u root -p'

def read_server_json():
    with open((os.path.join(onedirup, server_json))) as backup_restore_file:
        print('file opened')
        global erpnext_server_data
        global servers
        global how_many_servers
        global server_data
        erpnext_server_data = json.load(backup_restore_file)
        servers = erpnext_server_data['ERPNext-servers_to_backup']
        how_many_servers = len(servers)
        server_data = servers[0]

def run_server_backups(servers):
    message = ''
    server_count = 1
    for p in servers:
        print('***** Server #' + str(server_count) + ' *****')
        print('Hostname: ' + p['hostname'])
        print('User: ' + p['user'])
        print('Password: ' + p['password'])
        print('mySSHK: ' + p['mySSHK'])
        print('mySSHK Passphrase: ' + p['mySSHK_passphrase'])
        print(nl)

        # Open the SSH connection
        ssh = paramiko.SSHClient() # Creates an SSHClient object instance to connect with
        # Add the locally available SSH Keys to the ssh connection object.
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())# no known_hosts error
        # ssh.load_system_host_keys()
        # Connect
        ssh.connect(hostname, username=user, passphrase=mySSHK_passphrase) #no password needed           ssh.connect(hostname, username=user, passphrase=password, password=password) # When using password only use this
        print('Successfully connected to %s' % hostname)

        # obtain database user and password
        # Access the content of a remote file containing JSON data.
        # We obtain the password for the database file
        try:
            sftp_client = ssh.open_sftp()
            remote_file = sftp_client.open(commands_dict['passwords_file'])
            json_data = json.load(remote_file)
            # print(str(json_data))
            mysql_pass = json_data['mysql_root_password']
            print(mysql_pass)
            remote_file.close()
        finally:
            remote_file.close()
        
        # Concatenate the command string for backing up the database
        sql_db_backup_cmd = mysql_dump + mysql_pass  + spc + commands_dict['db_name'] + spc + '> ' + server_data['backup_dir'] + fwd + server_data['backup_filename'] + sql
        #print(str(sql_db_backup_cmd))

        # We now backup the database
        stdin, stdout, stderr = ssh.exec_command(sql_db_backup_cmd)
        channel = stdout.channel
        status = channel.recv_exit_status()
        if status == 0:
            
            for line in stdout.read().splitlines():
                result = str(line, 'utf-8')
                db_json = json.loads(result)
                print(str(db_json['mysql_root_password']))
            message = 'Database password successfully obtained'
        else:
            message = "Error obtaining database user and password"
            print(message)
        ssh.close()
        server_count += 1
    return message

print(header1 + spc + title + spc + header1)

try:
    read_server_json()
    # print(str(erpnext_server_data))
    # Setup the connection credentials before connection
    hostname = server_data['hostname']
    user = server_data['user']
    password = server_data['password']
    mySSHK = server_data['mySSHK']
    mySSHK_passphrase = server_data['mySSHK_passphrase']
    
    # Will read how many servers must be backed up
    print(header1 + spc + json_read + spc + header1)
    if how_many_servers == 1:
        print(header1 + spc + str(how_many_servers) + spc + one_stb + spc + header1)
    else:
        print(header1 + spc + str(how_many_servers) + spc + many_stb + spc + header1)
    result = run_server_backups(servers)
    print(str(result))
except:
    print('Something failed, could not execute remote server database backup')
finally:
    print('SQL Backup Process Completed')


