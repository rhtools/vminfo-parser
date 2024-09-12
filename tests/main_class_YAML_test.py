import io
import sys
import typing as t
import unittest

from vminfo_parser import main


class TestVMInfoParser(unittest.TestCase):

    def setUp(self: t.Self) -> None:
        # Create an in-memory text stream
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    def tearDown(self: t.Self) -> None:
        # Restore the original stdout
        sys.stdout = sys.__stdout__

    def test_get_supported_os_both_envs(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/supported_os_both_envs.yaml"
            ],
            "Environment               non-prod   prod\n"
            "OS Name\n"
            "Microsoft Windows              399   6881\n"
            "Microsoft Windows Server      3614  10118\n"
            "Red Hat Enterprise Linux       437    713\n"
            "SUSE Linux Enterprise          644   1347",
        )

    def test_get_supported_os_all_envs(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/supported_os_all_envs.yaml"
            ],
            "OS Name\n"
            "Microsoft Windows Server    13732\n"
            "Microsoft Windows            7280\n"
            "SUSE Linux Enterprise        1991\n"
            "Red Hat Enterprise Linux     1150",
        )

    def test_get_supported_os_non_prod(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/supported_os_non_prod.yaml"
            ],
            "OS Name\n"
            "Microsoft Windows Server    3614\n"
            "SUSE Linux Enterprise        644\n"
            "Red Hat Enterprise Linux     437\n"
            "Microsoft Windows            399",
        )

    def test_get_supported_os_minimum_count(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/supported_os_min_count.yaml"
            ],
            "OS Name\n"
            "Microsoft Windows Server    13732\n"
            "Microsoft Windows            7280\n"
            "SUSE Linux Enterprise        1991\n"
            "Red Hat Enterprise Linux     1150",
        )

    def test_get_unsupported_os(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/unsupported_os_both.yaml"
            ],
            "OS Name\n"
            "Ubuntu Linux    16583\n"
            "Oracle Linux    10589\n"
            "CentOS            592\n"
            "Other             671",
        )

    def test_get_os_counts(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/get_os_min_counts.yaml"
            ],
            "OS Name\n"
            "Ubuntu Linux                16583\n"
            "Microsoft Windows Server    13732\n"
            "Oracle Linux                10589\n"
            "Microsoft Windows            7280\n"
            "SUSE Linux Enterprise        1991\n"
            "Red Hat Enterprise Linux     1150\n"
            "CentOS                        592",
        )

    def test_disk_space_ranges_both_envs(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/disk_space_range_both_env.yaml"
            ],
            "Environment                            non-prod   prod       \n"
            "0-200 GB                               2312       5082      \n"
            "201-400 GB                             6176       12970     \n"
            "401-600 GB                             3338       5232      \n"
            "601-900 GB                             1828       6744      \n"
            "901-1500 GB                            1039       3580      \n"
            "1501-2000 GB                           253        658       \n"
            "2001-3000 GB                           1398       915       \n"
            "3001-5000 GB                           338        821       \n"
            "5001-9000 GB                           131        1006      \n"
            "9001-114256 GB                         65         707",
        )

    def test_disk_space_ranges_prod_env(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/disk_space_range_prod_env.yaml"
            ],
            "Environment                            prod       \n"
            "0-200 GB                               5082      \n"
            "201-400 GB                             12970     \n"
            "401-600 GB                             5232      \n"
            "601-900 GB                             6744      \n"
            "901-1500 GB                            3580      \n"
            "1501-2000 GB                           658       \n"
            "2001-3000 GB                           915       \n"
            "3001-5000 GB                           821       \n"
            "5001-9000 GB                           1006      \n"
            "9001-114256 GB                         707",
        )

    def test_disk_space_ranges_prod_env_by_terabyte(self: t.Self) -> None:
        self.run_test_with_args(
            [
                "--yaml",
                "tests/files/disk_space_range_prod_env_by_terabyte.yaml"
            ],
            "Environment                            prod       \n"
            "0-2000 GB                              34621     \n"
            "2001-9000 GB                           2805      \n"
            "9001-114256 GB                         707",
        )

    def run_test_with_args(self: t.Self, args: list[str], expected_output: str) -> None:
        try:
            # Run the main function with sample arguments
            main(*args)

            # Get the output
            output = self.captured_output.getvalue().strip()

            # Add your assertions here
            self.assertIn(expected_output, output)
        finally:
            # Clear the captured output for the next test
            self.captured_output.seek(0)
            self.captured_output.truncate()


if __name__ == "__main__":
    unittest.main()
