"""Command Line tool for running statistics over debian contents file."""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple

from columnar import columnar

from src.debian_package_stats.deb_dl_mgr import DebDLMgr, DebDLError
from src.debian_package_stats.contents_stat_mgr import (
    DebContentsStatMgr,
    DebianContentsFileNotFoundError,
)


# debian mirror to download files from
DEBIAN_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main"
# local download directory
DL_DIR = Path("/tmp")
# default number of top packages to show
DEFAULT_NUM_OF_TOP_PKGS = 10


def print_top_packages(top_packages: List[Tuple[str, int]]) -> None:
    """Print top packages.

    Format:
    1. <package name 1>         <number of files>
    2. <package name 2>         <number of files>
                           .
                           .
                           .
    #. <package name #>         <number of files>

    Args:
        top_packages (List[Tuple[str, int]): list of tuples that includes
            package name and number of files associate with it.
    """
    pkgs_table = []
    for i, (pkg_name, n) in enumerate(top_packages):
        pkgs_table.append([f"{i+1}.", pkg_name, n])

    print(columnar(pkgs_table, no_borders=True))


def download_contents_file(
    arch: str, mirror: str = DEBIAN_MIRROR, dl_dir: Path = DL_DIR
) -> Path:
    """Download contents file (by arch) from mirror server to local dir.

    Args:
        arch (str): given architecture to download.
        mirror (str): debian mirror server address.
        dl_dir (Path): path for local downloads directory.

    Returns:
        pathlib.Path: the local path of downloaded file.
    """

    try:
        dl_mgr = DebDLMgr(mirror, dl_dir)
        return dl_mgr.download_contents_file(arch=arch)

    except DebDLError as err:
        print(
            "The following error occured during the download"
            f"process for {arch}: {err}.",
            file=sys.stderr,
        )
        sys.exit(1)


def run_statistics(
    local_contents_file_path: Path, n: int
) -> List[Tuple[str, int]]:
    """Run statistics over file and return top packages.

    Args:
        local_contents_file_path (Path): path for local contents file.
        n (int): number of top packages to find.

    Returns:
        List[Tuple[str, int]]: list of tuples where each tuple consists of
                               a package name and the number of files
                               associated with it.
    """
    stat_mgr = DebContentsStatMgr(local_contents_file_path)

    try:
        # get top packages
        return stat_mgr.get_n_top_packages(n=n, use_cache=False)

    except DebianContentsFileNotFoundError as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    """Download contents file for given architecture and print top packages."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "arch", type=str, help="architecture[e.g. amd64, arm64, mips etc.]"
    )
    parser.add_argument(
        "--num-packages",
        type=int,
        default=DEFAULT_NUM_OF_TOP_PKGS,
        help="number of top packages to show",
    )
    args = parser.parse_args()

    local_contents_file_path = download_contents_file(args.arch)
    top_packages = run_statistics(local_contents_file_path, args.num_packages)
    print_top_packages(top_packages)
