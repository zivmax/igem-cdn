import os
import argparse
import json
from src.uploads import Session
import re

local_root = ""
args = None


def is_file_path(path: str) -> bool:
    # This regex checks if the path ends with a common file extension
    file_pattern = re.compile(r".+\.[a-zA-Z0-9]{1,5}$")
    return bool(file_pattern.match(path))


def is_dir_path(path: str) -> bool:
    # This regex checks if the path ends with a slash or has no file extension
    directory_pattern = re.compile(r".+/$|^[^\.]+$")
    return bool(directory_pattern.match(path))


def handle_missing(path: str) -> None:
    # If no server directory, create one
    if not os.path.exists(local_root):
        os.makedirs(local_root)

    if not os.path.exists(os.path.join(local_root, path)):
        if is_dir_path(os.path.join(local_root, path)):
            os.makedirs(os.path.join(local_root, path))
        elif is_file_path(os.path.join(local_root, path)):
            # Create a empty new file, add text in it to prompt user
            # that seeing the prompt means request failed.
            with open(os.path.join(local_root, path), "w") as f:
                f.write("Request failed. Please try again.")


def delete(client: Session, remote_path: str) -> None:
    if is_file_path(os.path.join(local_root, remote_path)):
        dir_path = os.path.dirname(remote_path)
        file_name = os.path.basename(remote_path)
        client.delete_file(file_name, dir_path, True)
    elif os.path.isdir(os.path.join(local_root, remote_path)):
        client.delete_dir(remote_path, args.recursive)
    else:
        print(f"Error: '{os.path.join(local_root, remote_path)}' does not exist.")


def sync_work_dir(client: Session, local_work_dir: str, remote_work_dir: str) -> None:
    """Upload all local files to remote without overwriting check, then download all remote files to local."""
    client.upload_dir(local_work_dir, remote_work_dir, True)
    client.download_dir(remote_work_dir, True)


def download(client: Session, remote_path: str) -> None:
    """Download from remote without overwriting check."""
    handle_missing(remote_path)
    if os.path.isfile(os.path.join(local_root, remote_path)):
        client.download_file(
            remote_path, os.path.dirname(os.path.join(local_root, remote_path)), True
        )
    elif os.path.isdir(os.path.join(local_root, remote_path)):
        client.download_dir(remote_path, local_root, args.recursive)
    else:
        print(f"Error: '{os.path.join(local_root, remote_path)}' does not exist.")


def upload(client: Session, local_path: str, remote_path: str) -> None:
    """Upload to remote without overwriting check."""
    if os.path.isfile(local_path):
        client.upload_file(local_path, os.path.dirname(remote_path), True)
    elif os.path.isdir(local_path):
        client.upload_dir(local_path, remote_path, args.recursive)
    else:
        print(f"Error: '{os.path.join(local_root, remote_path)}' does not exist.")


def load_config(config_path="config.json") -> dict:
    """Loads the configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def get_default_remote_path(local_path):
    """Calculates the default remote directory based on the local root."""
    rel = os.path.relpath(local_path, local_root)
    return rel if rel != "." else ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="iGEM CDN File and Directory Management CLI"
    )
    parser.add_argument(
        "action",
        choices=["delete", "sync", "download", "upload", "query"],
        help="Action to perform",
    )
    parser.add_argument("local_path", help="Local path")
    parser.add_argument("-rp", "--remote-path", help="Remote path")
    parser.add_argument("--config", help="Path to the configuration file")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively upload/download directories",
    )

    global args
    args = parser.parse_args()

    config = args.config
    remote_path = args.remote_path
    local_path = args.local_path

    if config is None:
        config = load_config(f"{os.getenv('HOME')}/.local/share/igem/config.json")
    else:
        config = load_config(config)

    if config is None:
        return

    username = config.get("username")["data"]
    password = config.get("password")["data"]
    global local_root
    local_root = config.get("local_root")["data"]
    if username is None or password is None:
        print(
            "Error: 'username' and 'password' must be specified in the configuration file."
        )
        return

    # Calculate default remote_path if not provided
    if remote_path is None:
        remote_path = get_default_remote_path(local_path)
    else:
        remote_path = remote_path.replace("server/", "")
        remote_path = remote_path.replace("server", "")

    client = Session()
    client.login(username, password)

    match args.action:
        case "delete":
            if not remote_path:
                print("Error: --remote-path is required for delete action")
                return
            delete(client, remote_path)
        case "sync":
            sync_work_dir(client, local_path, remote_path)
        case "download":
            download(client, remote_path)
        case "upload":
            upload(client, local_path, remote_path)
        case "query":
            client.query(remote_path)


if __name__ == "__main__":
    main()
