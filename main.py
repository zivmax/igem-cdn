import os
import argparse
import json
from src.uploads import Session


def delete_file_or_dir(client: Session, remote_dir: str) -> None:
    if os.path.isfile(remote_dir):
        client.delete(remote_dir)
    else:
        client.delete_dir(remote_dir)


def sync_work_dir(client: Session, local_work_dir: str, remote_work_dir: str) -> None:
    """Upload all local files to remote without overwriting check, then download all remote files to local."""
    client.upload_dir(local_work_dir, remote_work_dir)
    client.download_dir(remote_work_dir, local_work_dir)


def download_remote_dir(client: Session, remote_dir: str, local_dir: str) -> None:
    """Download local directory to remote directory without overwriting check."""
    client.download_dir(remote_dir, local_dir)


def upload_local_dir(client: Session, local_dir: str, remote_dir: str) -> None:
    """Upload local directory to remote directory without overwriting check."""
    client.upload_dir(local_dir, remote_dir)


def load_config(config_path="config.json"):
    """Loads the configuration from a JSON file."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None


def get_default_remote_dir(local_dir):
    """Calculates the default remote directory based on the local path."""
    return os.path.relpath(local_dir, os.getcwd())


def main() -> None:
    parser = argparse.ArgumentParser(description="File and Directory Management CLI")
    parser.add_argument(
        "action",
        choices=["delete", "sync", "download", "upload"],
        help="Action to perform",
    )
    parser.add_argument("--remote-dir", help="Remote directory path")
    parser.add_argument("--local-dir", help="Local directory path")
    parser.add_argument(
        "--config", default="config.json", help="Path to the configuration file"
    )

    args = parser.parse_args()
    config = load_config(args.config)

    if config is None:
        return

    username = config.get("username")
    password = config.get("password")
    if username is None or password is None:
        print(
            "Error: 'username' and 'password' must be specified in the configuration file."
        )
        return

    # Calculate default remote_dir if not provided
    if not args.remote_dir:
        if args.action != "delete":  # 'delete' doesn't use local_dir
            if not args.local_dir:
                print(
                    f"Error: --local-dir is required for {args.action} action when --remote-dir is not specified."
                )
                return
            args.remote_dir = get_default_remote_dir(args.local_dir)
        else:
            args.remote_dir = ""  # Default to root if not provided for delete

    client = Session()
    client.login(username, password)

    if args.action == "delete":
        if not args.remote_dir:
            print("Error: --remote-dir is required for delete action")
            return
        delete_file_or_dir(client, args.remote_dir)
    elif args.action == "sync":
        sync_work_dir(client, args.local_dir, args.remote_dir)
    elif args.action == "download":
        download_remote_dir(client, args.remote_dir, args.local_dir)
    elif args.action == "upload":
        upload_local_dir(client, args.local_dir, args.remote_dir)


if __name__ == "__main__":
    main()
