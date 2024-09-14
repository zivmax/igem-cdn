import os
import argparse
import json
from src.uploads import Session

def delete(client: Session, remote_path: str) -> None:
    if os.path.isfile("static/" + remote_path):
        dir_path = os.path.dirname(remote_path)
        file_name = os.path.basename(remote_path)
        client.delete_file(file_name, dir_path, True)
    elif os.path.isdir("static/" + remote_path):
        client.delete_dir(remote_path, True)
    else:
        print(f"Error: {remote_path} does not exist.")

def sync_work_dir(client: Session, local_work_dir: str, remote_work_dir: str) -> None:
    """Upload all local files to remote without overwriting check, then download all remote files to local."""
    client.upload_dir(local_work_dir, remote_work_dir, True)
    client.download_dir(remote_work_dir, True)


def download(client: Session, remote_path: str) -> None:
    """Download from remote without overwriting check."""
    # If it's a file
    if os.path.isfile("static/" + remote_path):
        client.download_file(remote_path, True)
    # If it's a directory
    elif os.path.isdir("static/" + remote_path):
        client.download_dir(remote_path, True)
    else:
        print(f"Error: {remote_path} does not exist.")

def upload(client: Session, local_path: str, remote_path: str) -> None:
    """Upload to remote without overwriting check."""
    # If it's a file
    if os.path.isfile(local_path):
        client.upload_file(local_path, remote_path, True)
    # If it's a directory
    elif os.path.isdir(local_path):
        client.upload_dir(local_path, remote_path, True)
    else:
        print(f"Error: {remote_path} does not exist.")

def load_config(config_path="config.json") -> dict:
    """Loads the configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def get_default_remote_path(local_root):
    """Calculates the default remote directory based on the local path."""
    return os.path.relpath(local_root, os.getcwd())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="iGEM CDN File and Directory Management CLI"
    )
    parser.add_argument(
        "action",
        choices=["delete", "sync", "download", "upload", "query"],
        help="Action to perform",
    )
    parser.add_argument("-rp", "--remote-path", help="Remote path")
    parser.add_argument("-lp", "--local-path", help="Local path")
    parser.add_argument("--config", help="Path to the configuration file")

    args = parser.parse_args()

    if args.config is None:
        config = load_config(f"{os.getenv('HOME')}/.local/bin/igem/config.json")
    else:
        config = load_config(args.config)

    if config is None:
        return

    username = config.get("username")["data"]
    password = config.get("password")["data"]
    local_root = config.get("local_root")["data"]
    if username is None or password is None:
        print(
            "Error: 'username' and 'password' must be specified in the configuration file."
        )
        return

    # Calculate default remote_path if not provided
    if args.remote_path is None:
        if args.action != "delete":  # 'delete' doesn't use local_path
            if not args.local_path:
                print(
                    f"Error: --local-path is required for {args.action} action when --remote-path is not specified."
                )
                return
            args.remote_path = get_default_remote_path(local_root)
        else:
            args.remote_path = ""  # Default to root if not provided for delete
    else:
        args.remote_path = args.remote_path.replace("static/", "")

    client = Session()
    client.login(username, password)

    match args.action:
        case "delete":
            if not args.remote_path:
                print("Error: --remote-path is required for delete action")
                return
            delete(client, args.remote_path)
        case "sync":
            sync_work_dir(client, args.local_path, args.remote_path)
        case "download":
            download(client, args.remote_path)
        case "upload":
            upload(client, args.local_path, args.remote_path)
        case "query":
            client.query(args.remote_path)


if __name__ == "__main__":
    main()
