import httpx
import mimetypes
import os
import prettytable as pt
import threading
from pathlib import Path
from sys import exit
import warnings
from tqdm import tqdm


NOT_LOGGED_IN = 0
LOGGED_IN = 1
LOGIN_FAILED = -1
TIMEOUT = 30
STATIC_URL_PREFIX = "https://static.igem.wiki/teams/"

def check_parameter(directory: str) -> None:
    """Check if the directory parameter is valid.

    Args:
        directory (str): The directory path to check.

    Raises:
        Warning: If the directory starts with '/'.
    """
    if directory.startswith("/"):
        warnings.warn(
            "You specified a directory name starting with '/', which may cause unknown errors"
        )
        exit(1)


class Session:
    """Class to manage the session for interacting with the iGEM API."""

    def __init__(self):
        self.client = httpx.Client(http2=True)
        self.status = NOT_LOGGED_IN
        self.team_id = ""
        self.url = ""

    def _request(
        self,
        method: str,
        url: str,
        params: dict = None,
        data: dict = None,
        files: dict = None,
    ) -> httpx.Response:
        """Make an HTTP request to the specified URL.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            url (str): The URL to send the request to.
            params (dict, optional): URL parameters to include in the request.
            data (dict, optional): Data to send in the body of the request.
            files (dict, optional): Files to upload.

        Returns:
            httpx.Response: The response object from the request.

        Raises:
            Warning: If the user is not logged in.
        """
        if self.status != LOGGED_IN:
            warnings.warn("Not logged in, please login first")
            exit(1)
        return self.client.request(
            method=method, 
            url=url, 
            params=params, 
            data=data, 
            files=files, 
            timeout=TIMEOUT
        )

    def _request_team_id(self) -> str:
        """Retrieve the team ID for the logged-in user.

        Returns:
            str: The team ID of the main team.

        Raises:
            Warning: If the user is not part of any team or if their team or role is not accepted.
        """
        response = self.client.get(
            "https://api.igem.org/v1/teams/memberships/mine",
            params={"onlyAcceptedTeams": True},
            timeout=TIMEOUT,
        )
        team_list = response.json()
        if len(team_list) == 0:
            warnings.warn("Not joined any team")
            exit(1)
        main_team = team_list[0]["team"]
        main_membership = team_list[0]["membership"]
        team_id = main_team["id"]
        team_name = main_team["name"]
        team_status = main_team["status"]
        team_year = main_team["year"]
        team_role = main_membership["role"]
        team_role_status = main_membership["status"]
        print("Team:", team_id, team_name, team_year)
        print("Role:", team_role)
        if team_status != "accepted":
            warnings.warn("Your team is not accepted")
        if team_role_status != "accepted":
            warnings.warn("Your team role is not accepted")
        return team_id

    def login(self, username: str, password: str) -> None:
        """Log in to the iGEM API.

        Args:
            username (str): Your username.
            password (str): Your password.

        Raises:
            Warning: If the credentials are invalid.
        """
        data = {"identifier": username, "password": password}
        try:
            print("Logging in...")
            response = self.client.post(
                "https://api.igem.org/v1/auth/sign-in", data=data, timeout=TIMEOUT
            )
            response.raise_for_status()  # Raises an HTTPStatusError for bad responses (4xx and 5xx)

            if "Invalid credentials" in response.text:
                self.status = LOGIN_FAILED
                warnings.warn("Invalid credentials")
                exit(1)
            else:
                self.status = LOGGED_IN
                self.team_id = self._request_team_id()
                self.url = STATIC_URL_PREFIX + str(self.team_id) + '/'

        except httpx.HTTPStatusError as http_err:
            self.status = LOGIN_FAILED
            warnings.warn(f"HTTP error occurred: {http_err}")
            exit(1)
        except httpx.RequestError as req_err:
            self.status = LOGIN_FAILED
            warnings.warn(f"Request failed: {req_err}")
            exit(1)

    def query(self, directory: str = "", output: bool = True) -> list:
        """Query files and directories in a specific directory.

        Args:
            directory (str, optional): The directory to query. Defaults to the root directory.
            output (bool, optional): Whether to print the query result. Defaults to True.

        Returns:
            list: A list of files, each represented as a dictionary.

        Raises:
            Warning: If the query fails.
        """
        check_parameter(directory)
        response = self._request(
            "GET",
            f"https://api.igem.org/v1/websites/teams/{self.team_id}",
            params={"directory": directory} if directory != "" else None,
        )

        # Check if the request was successful
        if response.status_code != 200:
            warnings.warn(f"Query failed with status code: {response.status_code}.")
            return []

        res = response.json()

        if res["KeyCount"] > 0:
            contents = []
            if res.get("CommonPrefixes", False):
                contents.extend(sorted(res["CommonPrefixes"], key=lambda x: x["Name"]))
            if res.get("Contents", False):
                contents.extend(
                    sorted(res["Contents"], key=lambda x: (x["Type"], x["Name"]))
                )
            table = pt.PrettyTable()
            table.field_names = ["Type", "Name", "DirectoryKey/FileURL"]
            for item in contents:
                if item["Type"] == "Folder":
                    table.add_row(
                        [
                            "Folder",
                            item["Name"],
                            item["Key"].split(f"teams/{self.team_id}/")[-1],
                        ]
                    )
                else:
                    table.add_row(
                        ["File-" + item["Type"], item["Name"], item["Location"]]
                    )
            if output:
                print(table)
                print(f"'{directory if directory != "" else "/"}' found: {res["KeyCount"]}")
            return contents
        elif res["KeyCount"] == 0:
            print(f"'{directory if directory != "" else "/"}'" , "found: 0")
            return []
        else:
            warnings.warn("Query failed")
            return []

    def upload_file(
        self, file_path: str, dest_dir: str = "", output: bool = False
    ) -> str:
        """Upload a file to a specific remote directory.

        Args:
            abs_file_path (str): Absolute path of the file to upload.
            directory (str, optional): The target directory. Defaults to the root directory.
            list_files (bool, optional): Whether to list files after upload. Defaults to True.

        Returns:
            str: The file URL of the uploaded file.

        Raises:
            Warning: If the file path is invalid or the upload fails.
        """
        check_parameter(dest_dir)
        if dest_dir == "/":
            warnings.warn(
                "You specified '/' as a directory name, which may cause unknown errors"
            )
            exit(1)
        path_to_file = Path(file_path)
        if not path_to_file.is_file():
            warnings.warn("Invalid file path: " + file_path)
            exit(1)
        mime_type = mimetypes.guess_type(file_path, True)[0]
        files = {"file": (path_to_file.name, open(file_path, "rb"), mime_type)}
        res = self._request(
            "POST",
            f"https://api.igem.org/v1/websites/teams/{self.team_id}",
            params={"directory": dest_dir} if dest_dir != "" else None,
            files=files,
        )
        if res.status_code == 201:
            if output:
                print(f"'{path_to_file.name}' uploaded {res.text}")
            return res.text
        else:
            warnings.warn(f"Upload '{path_to_file.name}' failed {res.text}")

    def upload_dir(self, local_dir: str, dest_dir: str = "", recursive: bool = False) -> list:
        """Upload the contents of a directory to a specific remote path.

        Args:
            local_dir (str): Path of the directory to upload.
            dest_dir (str, optional): The target directory. Defaults to the root directory.
            recursive (bool, optional): Whether to upload subdirectories. Defaults to True.

        Raises:
            Warning: If the directory path is invalid.
        """
        def collect_files_and_dirs(directory_path):
            path_to_dir = Path(directory_path)
            if not path_to_dir.is_dir():
                return [], []

            file_list = []
            dir_list = []
            for item in path_to_dir.iterdir():
                if item.is_dir():
                    dir_list.append(item)
                    if recursive:  # Only collect subdirectories if recursive is True
                        sub_files, sub_dirs = collect_files_and_dirs(item)
                        file_list.extend(sub_files)
                        dir_list.extend(sub_dirs)
                elif not item.name.startswith("."):
                    file_list.append(item)
            return file_list, dir_list

        check_parameter(dest_dir)
        if dest_dir == "/":
            warnings.warn(
                "You specified '/' as a directory name, which may cause unknown errors"
            )
            exit(1)
        path_to_dir = Path(local_dir)
        if not path_to_dir.is_dir():
            warnings.warn(f"Invalid directory path: '{local_dir}'")
            exit(1)

        all_files, all_dirs = collect_files_and_dirs(local_dir)

        if not all_files and not all_dirs:
            print(f"Directory '{local_dir}' is empty")
            return []

        lock = threading.Lock()

        self.successful_uploads = 0
        def thread_upload(file_path, remote_dir_path):
            try:
                self.upload_file(file_path, remote_dir_path, False)
                with lock:
                    self.successful_uploads += 1
                    pbar.update(1)  # Update progress bar
            except Exception as e:
                print(f"Error uploading '{file_path}': {e}")

        remote_base_dir = dest_dir if dest_dir else path_to_dir.name

        # Use tqdm to create a progress bar
        with tqdm(total=len(all_files), desc="Uploading files", unit="file") as pbar:
            threads: list[threading.Thread] = []
            for file_path in all_files:
                relative_file_path = file_path.relative_to(local_dir)
                remote_file_dir = os.path.join(remote_base_dir, relative_file_path.parent)
                thread = threading.Thread(
                    target=thread_upload,
                    args=(str(file_path), remote_file_dir),
                )
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        print(f"Uploaded {self.successful_uploads} files to '{os.path.join(dest_dir, '')}'\n")


    def delete_file(self, filename: str, directory: str = "", output: bool = False) -> None:
        """Delete a file in a specific directory.

        Args:
            filename (str): The name of the file to delete.
            directory (str, optional): The parent directory of the file. Defaults to the root directory.
            output (bool, optional): Whether to list files after deletion. Defaults to True.

        Raises:
            Warning: If the deletion fails.
        """
        check_parameter(directory)
        if directory == "/":
            warnings.warn(
                "You specified '/' as a directory name, which may cause unknown errors"
            )
            exit(1)
        res = self._request(
            "DELETE",
            f"https://api.igem.org/v1/websites/teams/{self.team_id}/{filename}",
            params={"directory": directory} if directory != "" else None,
        )
        if res.status_code == 200:
            if output:
                print(f"'{os.path.join(directory, filename)}' deleted")
        else:
            warnings.warn(f"'{os.path.join(directory, filename)}' delete failed")

    def delete_dir(self, directory: str, recursive: bool = False) -> None:
        """Delete a directory by deleting its contents.

        Args:
            directory (str): The directory to delete.
            recursive (bool): Whether to delete subdirectories as well.

        Raises:
            Warning: If attempting to delete the root directory.
        """
        if directory == "":
            warnings.warn(
                "Trying to delete the root directory! Please specify a directory name instead."
            )
            exit(1)

        if len(self.query(directory, output=False)) == 0:
            warnings.warn(f"Directory '{directory}' is empty")
            return

        stack = [directory]
        all_items = []
        successful_deletions = 0

        # Collect all items first
        while stack:
            current_dir = stack.pop()
            contents = self.query(current_dir, output=False)                
            for item in contents:
                all_items.append((current_dir, item))
                if item["Type"] == "Folder" and recursive:  # Only add to stack if recursive is True
                    stack.append(os.path.join(current_dir, item["Name"]))

        # Process all items with a single progress bar
        with tqdm(
            total=len(all_items), desc="Deleting directory", unit="item"
        ) as pbar:
            for current_dir, item in all_items:
                if item["Type"] != "Folder" or (item["Type"] == "Folder" and recursive):
                    self.delete_file(item["Name"], current_dir, False)
                    successful_deletions += 1
                pbar.update(1)

        print(f"Deleted '{os.path.join(directory, '')}' with {successful_deletions} files\n")


    def download_file(self, file_url: str, target_dir: str = "", output: bool = False) -> bool:
        """Download a single file from a URL.

        Args:
            file_url (str): The URL of the file to download.
            target_dir (str, optional): The target directory for saving the file. Defaults to the current directory.

        Returns:
            bool: True if the download was successful, False otherwise.
        """
        if not file_url.startswith(STATIC_URL_PREFIX):
            file_url = self.url + file_url
        file_name = os.path.basename(file_url)  # get file name from url
        file_path = os.path.join(target_dir, file_name)  # local file path

        headers = {
            "Host": "static.igem.wiki",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers",
        }

        try:
            with httpx.Client(http2=True, headers=headers) as client:
                response = client.get(file_url, timeout=TIMEOUT)

            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
                if output:
                    print(f"Downloaded '{file_url}' to '{file_path}'")
                return True
            else:
                print(
                    f"Failed to download '{file_url}': Response Header {response.headers}"
                )
                return False
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            exit(1)

    def download_dir(self, remote_dir: str = "", target_dir: str = "server", recursive: bool = False) -> None:
        """Download a directory and its subdirectories to the local file system."""

        def collect_files(directory, recursive):
            contents = self.query(directory, False)
            if not contents:
                return []

            file_list = []
            for item in contents:
                if item["Type"] == "Folder":
                    if recursive:
                        file_list.extend(
                            collect_files(
                                item["Prefix"].split(f"teams/{self.team_id}/")[1],
                                recursive,
                            )
                        )
                else:
                    file_list.append((item["Location"], directory))
            return file_list

        self.successful_downloads = 0
        self.query(remote_dir)
        all_files = collect_files(remote_dir, recursive)

        if not all_files:
            print(f"Directory '{remote_dir}' is empty")
            return

        for file_url, dir_path in all_files:
            local_target_directory = f"{target_dir}/{dir_path}"
            os.makedirs(local_target_directory, exist_ok=True)

        # Create a lock for thread-safe updates
        lock = threading.Lock()

        def thread_download(file_url, dir_path):
            try:
                self.download_file(file_url, dir_path)
                with lock:
                    self.successful_downloads += 1
                    pbar.update(1)  # Update progress bar
            except Exception as e:
                print(f"Error downloading '{file_url}': {e}")

        # Use tqdm to create a progress bar
        with tqdm(total=len(all_files), desc="Downloading files", unit="file") as pbar:
            threads = []
            for file_url, dir_path in all_files:
                local_target_directory = f"{target_dir}/{dir_path}"
                thread = threading.Thread(
                    target=thread_download,
                    args=(file_url, local_target_directory),
                )
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        remote_dir = remote_dir if remote_dir != "" else "/"
        print(f"Downloaded {self.successful_downloads} files in '{os.path.join(remote_dir, "")}'\n")
