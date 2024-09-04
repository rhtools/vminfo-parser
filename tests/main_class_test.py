import unittest
import io
import sys
from contextlib import redirect_stdout
from ..vminfo_parser import main

class TestVMInfoParser(unittest.TestCase):

    def setUp(self):
        # Create an in-memory text stream
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        # Restore the original stdout
        sys.stdout = sys.__stdout__

    def test_get_supported_os_both_envs(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-supported-os",
            "--sort-by-env", "both",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'Environment               non-prod   prod\nOS Name\nMicrosoft Windows              399   6881\nMicrosoft Windows Server      3614  10118\nRed Hat Enterprise Linux       437    713\nSUSE Linux Enterprise          644   1347')

    def test_get_supported_os_all_envs(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-supported-os",
            "--sort-by-env", "all",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'OS Name\nMicrosoft Windows Server    13732\nMicrosoft Windows            7280\nSUSE Linux Enterprise        1991\nRed Hat Enterprise Linux     1150')

    def test_get_supported_os_non_prod(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-supported-os",
            "--sort-by-env", "non-prod",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'OS Name\nMicrosoft Windows Server    3614\nSUSE Linux Enterprise        644\nRed Hat Enterprise Linux     437\nMicrosoft Windows            399')

    def test_get_supported_os_minimum_count(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-supported-os",
            "--minimum-count", "500",
            "--sort-by-env", "all",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'OS Name\nMicrosoft Windows Server    13732\nMicrosoft Windows            7280\nSUSE Linux Enterprise        1991\nRed Hat Enterprise Linux     1150')
    
    def test_get_unsupported_os(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-unsupported-os",
            "--minimum-count", "500",
            "--sort-by-env", "both",
            "--prod-env-labels", "Prod-DC2,Prod-DC1",
        ], 'OS Name\nUbuntu Linux    16583\nOracle Linux    10589\nCentOS            592\nOther             671')
    
    def test_get_os_counts(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-os-counts",
            "--minimum-count", "500"
        ], 'OS Name\nUbuntu Linux                16583\nMicrosoft Windows Server    13732\nOracle Linux                10589\nMicrosoft Windows            7280\nSUSE Linux Enterprise        1991\nRed Hat Enterprise Linux     1150\nCentOS                        592')
    
    def test_disk_space_ranges_both_envs(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-disk-space-ranges",
            "--sort-by-env", "both",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'Environment                            non-prod   prod       \n0-200 GB                               2312       5082      \n201-400 GB                             6176       12970     \n401-600 GB                             3338       5232      \n601-900 GB                             1828       6744      \n901-1500 GB                            1039       3580      \n1501-2000 GB                           253        658       \n2001-3000 GB                           1398       915       \n3001-5000 GB                           338        821       \n5001-9000 GB                           131        1006      \n9001-114256 GB                         65         707')
    
    def test_disk_space_ranges_prod_env(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-disk-space-ranges",
            "--sort-by-env", "prod",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'Environment                            prod       \n0-200 GB                               5082      \n201-400 GB                             12970     \n401-600 GB                             5232      \n601-900 GB                             6744      \n901-1500 GB                            3580      \n1501-2000 GB                           658       \n2001-3000 GB                           915       \n3001-5000 GB                           821       \n5001-9000 GB                           1006      \n9001-114256 GB                         707')
    
    def test_disk_space_ranges_prod_env_by_terabyte(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-disk-space-ranges",
            "--sort-by-env", "prod",
            "--prod-env-labels", "Prod-DC2,Prod-DC1",
            "--breakdown-by-terabyte"
        ], 'Environment                            prod       \n0-2000 GB                              34621     \n2001-9000 GB                           2805      \n9001-114256 GB                         707')


    def run_test_with_args(self, args, expected_output):
        try:
            # Run the main function with sample arguments
            main(args)
            
            # Get the output
            output = self.captured_output.getvalue().strip()
            
            # Add your assertions here
            self.assertIn(expected_output, output)
        finally:
            # Clear the captured output for the next test
            self.captured_output.seek(0)
            self.captured_output.truncate()

if __name__ == '__main__':
    unittest.main()