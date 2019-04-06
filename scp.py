import subprocess

spc = ' '
nl = '\n'
fwd = '/'
at = '@'
colon = ':'

def scp_remote_to_local(hostname, user, remote_path_and_filename, local_path):
    scp_copy_from_command = 'sudo scp' + spc + user + at + hostname + colon + remote_path_and_filename + spc + local_path
    print(str(scp_copy_from_command))
    # subprocess.run(["ls", "-l"])
    subprocess.run(["scp", str(user + at + hostname + colon + remote_path_and_filename), str(local_path)])
def scp_local_to_remote(hostname, user, remote_path, local_path_and_filename):
    scp_copy_to_command = 'sudo scp' + spc + local_path_and_filename + spc + user + at + hostname + colon + remote_path + fwd
    print(str(scp_copy_to_command))
    subprocess.run(["scp", str(local_path_and_filename), str(user + at + hostname + colon + remote_path + fwd)])

# WORKS GREAT!
# scp_remote_to_local(hostname, user, remote_path_and_filename, local_dir)
# WORKS GREAT!
# scp_local_to_remote(hostname, user, remote_path, local_path_and_filename)
