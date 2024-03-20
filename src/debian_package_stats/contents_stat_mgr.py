"""Statistics manager for contents indices file."""

import os
import gzip
from pathlib import Path
from typing import List, Tuple


class DebianContentsFileNotFoundError(Exception):
    pass


class DebContentsStatMgr:
    """Statistics manager for contents indices file.

    File structure:

    FILE            LOCATION
    filename        package1, package2,...
    filename        package1, package2,...
    filename        package1, package2,...
                .
                .
                .

    Valid package structure: [[$AREA/]$SECTION/]$NAME
    - $AREA is the archive area
    - $SECTION the package section
    - $NAME the name of the package
    """

    def __init__(self, file_path: Path) -> None:
        """Initialize new statistics manager with local contents file path.

        Args:
            file_path (Path): local contents indices file path.
        """
        self._file_path = file_path
        self._package_files_hist = dict()

    def _count_files_for_pkg(self):
        """Count how many files each package point to."""
        with gzip.open(self._file_path, "rt") as contets_file:
            for line in contets_file:
                # package names cannot include white space characters
                pkgs = line.strip().rpartition(" ")[-1]
                # get packages names using scheme [[$AREA/]$SECTION/]$NAME
                for pkg in pkgs.split(","):
                    _, _, pkg_name = pkg.rpartition("/")
                    if pkg_name in self._package_files_hist:
                        self._package_files_hist[pkg_name] += 1
                    else:
                        self._package_files_hist[pkg_name] = 1

    def get_n_top_packages(
        self, n: int, use_cache: bool = True
    ) -> List[Tuple[str, int]]:
        """Return top n packages that have the most files associated with them.

        Args:
            n (int): number of top packages to return.
            use_cache (bool): indicates if to use manager histogram in case
                              it exists.

        Returns:
            List[Tuple[str, int]]: list of tuples where each tuple consists of
                                   a package name and the number of
                                   files associated with it.

        Raises:
            DebianContentsFileNotFoundError: in case local contents file does
                                             not exist.
        """
        # verify there is a local file
        if not os.path.isfile(self._file_path):
            raise DebianContentsFileNotFoundError(
                f"Contents file was not found at {self._file_path}.\n"
                "Please download it in order to continue."
            )

        elif not use_cache or not self._package_files_hist:
            self._count_files_for_pkg()

        return sorted(
            self._package_files_hist.items(), key=lambda t: t[1], reverse=True
        )[:n]
