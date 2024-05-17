import daq_connectivity as daq

remote_name = 'first_remote'
remote_type = 'drive'
in_path = 'results'
out_path = f'{remote_name}:Eurecat'
list_of_remotes = daq.list_remotes()

if list_of_remotes:
    for e in list_of_remotes:
        daq.delete_remote(e)

daq.create_remote(remote_name, remote_type)
# refresh_remote(remote_name)
daq.copy_to_remote(in_path, out_path)
