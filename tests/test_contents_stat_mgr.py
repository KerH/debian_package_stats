"""Test statistics manager for contents indices file."""

import pytest
from typing import List, Tuple
from unittest.mock import patch, mock_open

from src.debian_package_stats.contents_stat_mgr import (
    DebContentsStatMgr,
    DebianContentsFileNotFoundError,
)


@pytest.fixture(scope="class")
def contents_indices() -> str:
    """Mock contents indices file."""
    return (
        "sbin/klogd                                utils/busybox-syslogd\n"
        "bin/logread                               utils/busybox-syslogd\n"
        "etc/insserv.conf.d/busybox-syslogd        utils/busybox-syslogd\n"
        "etc/init.d/swift-object                   net/swift-object\n"
        "etc/init.d/swift-object-auditor           net/swift-object\n"
        "etc/init.d/tlp                            utils/tlp\n"
    )


@pytest.mark.usefixtures("contents_indices")
class TestDebContentsStatMgr:
    @pytest.mark.parametrize(
        "n, pkgs",
        [
            (3, [("busybox-syslogd", 3), ("swift-object", 2), ("tlp", 1)]),
            (2, [("busybox-syslogd", 3), ("swift-object", 2)]),
            (1, [("busybox-syslogd", 3)]),
        ],
    )
    def test_get_n_top_packages(
        self, n: int, pkgs: List[Tuple[str, int]], contents_indices: str
    ):
        """Test getting the correct top n packages from contents file.

        Args:
            n (int): number of top packages
            pkgs (List[Tuple[str, int]]): list of tuples that include
                                          the package name and the number
                                          of files associated with it.
            contents_indices (str): fixture that's mimicking contents indices.
        """
        stat_mgr = DebContentsStatMgr("")
        # test raise error when no file exists
        with pytest.raises(DebianContentsFileNotFoundError):
            stat_mgr.get_n_top_packages(n)
        # test top packages statistics
        with patch("gzip.open", mock_open(read_data=contents_indices)), patch(
            "os.path.isfile", return_value=True
        ):
            assert stat_mgr.get_n_top_packages(n, use_cache=False) == pkgs
