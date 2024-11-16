# iGEM CDN Tool

## Create Config File

Run the following command in the terminal:

```shell
curl -o- https://raw.githubusercontent.com/zivmax/igem-cdn/refs/heads/main/config-remote.sh | bash
```

Then VSCode should pop up for you to fill a template:

```
{
    "username": {
        "data": "your_username"
    },
    "password": {
        "data": "your_password"
    },
    "local_root": {
        "data": "/path/to/your/local/server"
    }
}
```

- Username: Your iGEM account username
- Password: Your iGEM account password
- Local Root:
  1. First, Create a folder named `server` in the root of the project.
     ![Create Server Folder](server/docs/vscode-folder-create.webp)
  1. Then, right-click the folder and select `Copy Path`.
     ![Copy Path](server/docs/vscode-copy-path.webp)
  1. Use the path you just copied as the value of `local_root` in `data` field.

Save the file by `Ctrl+S`or `Cmd+S`.

## Install CDN Tool

First, ensure you can `unzip` things, MacOS user should have it installed by default, for WSL / Linux user, run:

```shell
sudo apt install zip
```

Run the following command in the terminal:

```shell
bash -c "$(curl -fsSL https://raw.githubusercontent.com/zivmax/igem-cdn/refs/heads/main/setup-remote.sh)" -- install
```

Restart the terminal after the installation, if you are using VSCode integrated terminal, restart VSCode.

## Test CDN Tool

Run the following command in the terminal:

```shell
igem-cdn
```

And you should see the help message of the tool.

```
usage: igem-cdn [-h] [-rp REMOTE_PATH] [--config CONFIG]
                {delete,sync,download,upload,query} local_path
igem-cdn: error: the following arguments are required: action, local_path
```
