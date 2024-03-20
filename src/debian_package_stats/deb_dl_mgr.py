"""Download manager for debian distribution index."""

import os
import urllib
from pathlib import Path

import requests


class DebDLError(Exception):
    pass


class DebDLMgr:
    def __init__(self, mirror: str, dl_dir: Path) -> None:
        """Initialize new download manager with debian mirror and local dir.

        Args:
            mirror (str): mirror server to download from.
            dl_dir (Path): local download directory path.

        Raises:
            DebDLError: in case an error occured when creating download
                        directory.
        """
        self._mirror = mirror
        self._dl_dir = dl_dir
        self._mkdir()

    def _mkdir(self):
        """Create download directory and handle errors.

        Raises:
            DebDLError: in case empty name received or there is a
                        permission error to create directory.
        """
        try:
            # os.makedirs does not support empty strings
            if not self._dl_dir:
                raise DebDLError("Empty download directory is not allowed.")
            # name is not empty, create the dir
            os.makedirs(self._dl_dir, exist_ok=True)
        except PermissionError as err:
            raise DebDLError(err)

    def download_contents_file(self, arch: str) -> Path:
        """Download contents file from mirror to local downloads directory.

        Args:
            arch (str): architecture file to download.

        Returns:
            pathlib.Path: local path of downloaded contents file.

        Raises:
            DebDLError: in case of failure to complete action.
        """
        url = urllib.parse.urlparse(f"{self._mirror}/Contents-{arch}.gz")
        try:
            response = requests.get(url.geturl())
            if response.status_code == urllib.request.http.HTTPStatus.OK:
                downloaded_file_path = self._dl_dir / Path(
                    url.path.split("/")[-1]
                )
                with open(downloaded_file_path, "wb") as gz_file:
                    gz_file.write(response.content)
                    return downloaded_file_path

            else:
                raise DebDLError(
                    f"Response returned with {response.status_code} "
                    "status code."
                )

        except (requests.exceptions.RequestException, OSError) as err:
            raise DebDLError(err)
