import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from uploads import Session

def upload_file(client, local_file_path, remote_file_path):
    remote_dir = os.path.dirname(remote_file_path)
    if remote_dir:
        client.upload(local_file_path, remote_dir)
    else:
        client.upload(local_file_path)

def upload_all_files(local_root, remote_root, max_workers=4):
    client = Session()
    
    # Replace 'your_username' and 'your_password' with your actual iGEM credentials
    client.login('your_username', 'your_password')
    
    files_to_upload = []
    for root, dirs, files in os.walk(local_root):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_root)
            remote_file_path = os.path.join(remote_root, relative_path)
            files_to_upload.append((local_file_path, remote_file_path))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(upload_file, client, local_file_path, remote_file_path): (local_file_path, remote_file_path) for local_file_path, remote_file_path in files_to_upload}
        
        for future in as_completed(future_to_file):
            local_file_path, remote_file_path = future_to_file[future]
            try:
                future.result()
                print(f'Successfully uploaded {local_file_path} to {remote_file_path}')
            except Exception as exc:
                print(f'Failed to upload {local_file_path} to {remote_file_path}: {exc}')

if __name__ == "__main__":
    # Replace 'local_root_directory' with the path to your local directory
    # Replace 'remote_root_directory' with the path to your remote directory
    local_root_directory = '.'
    remote_root_directory = 'test/upload-test'
    
    upload_all_files(local_root_directory, remote_root_directory)
