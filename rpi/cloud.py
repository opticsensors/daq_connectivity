import dropbox

# Access token from Dropbox App
dbx = dropbox.Dropbox('YOUR_ACCESS_TOKEN')

def upload_file(file_path, target_path):
    with open(file_path, 'rb') as f:
        dbx.files_upload(f.read(), target_path, mode=dropbox.files.WriteMode.overwrite)

# Example usage
upload_file('/results/2024-05-16_11.12.06.035455.csv', '/Apps/YourAppFolder/file.csv')