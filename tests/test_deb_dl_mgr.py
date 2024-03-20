"""Test DebDLMgr class behavior."""

import pytest
import shutil
from pathlib import Path

from src.debian_package_stats.deb_dl_mgr import DebDLMgr


class TestDebDLMgr:
    DL_DIR = Path("/tmp/tests_downloads")
    DEBIAN_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main"

    @classmethod
    def setup_class(cls):
        """Create download manager for tests."""
        cls.dl_mgr = DebDLMgr(cls.DEBIAN_MIRROR, cls.DL_DIR)

    @classmethod
    def teardown_class(cls):
        """Remove downloads directory."""
        shutil.rmtree(cls.DL_DIR, ignore_errors=True)

    @pytest.mark.parametrize(
        "arch",
        [
            "amd64",
            "arm64",
            "armel",
            "armhf",
            "i386",
            "mips64el",
            "mipsel",
            "ppc64el",
            "s390x",
            "udeb-amd64",
            "udeb-arm64",
            "udeb-armel",
            "udeb-armhf",
            "udeb-i386",
            "udeb-mips64el",
            "udeb-mipsel",
            "udeb-ppc64el",
            "udeb-s390x",
            "all",
            "udeb-all",
        ],
    )
    def test_download_contents_file(self, arch: str):
        """Verify that contents file was downloaded to expected location.

        Args:
            arch (str): architecture file to download.
        """
        assert self.dl_mgr.download_contents_file(arch) == self.DL_DIR / Path(
            f"Contents-{arch}.gz"
        )
