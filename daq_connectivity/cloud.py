import subprocess
# rclone need to be installed first!

def create_remote(remote_name, remote_type):
    """
    This will open a window and we have to authorize
    """
    cmd = f"rclone config create {remote_name} {remote_type} env_auth=true"
    subprocess.run(cmd, shell=True, text=True, capture_output=True)

def refresh_remote(remote_name):
    """
    Get a new token 
    """
    cmd = f"rclone config reconnect {remote_name}"
    subprocess.run(cmd, shell=True, text=True, capture_output=True)

def copy_to_remote(in_path, out_path):
    """
    in_path is the folder/file we want to copy to out_path 
    if path is remote, it should be remote_name:path
    """

    cmd = f"rclone copy {in_path} {out_path}"
    subprocess.run(cmd, shell=True, text=True, capture_output=True)

def delete_remote(remote_name):
    """
    """
    cmd = f"rclone config delete {remote_name}"
    subprocess.run(cmd, shell=True, text=True, capture_output=True)

def list_remotes():
    cmd = 'rclone listremotes'
    sp = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    string_of_remotes = sp.stdout.decode()
    # Splitting the string at each newline character to create a list
    list_of_remotes = string_of_remotes.split('\n')
    # Removing the colon from each item and filtering out any empty strings
    list_of_remotes = [item.replace(':', '') for item in list_of_remotes if item]
    return list_of_remotes

