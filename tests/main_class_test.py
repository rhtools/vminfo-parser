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

    def test_main_output_both_envs(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-supported-os",
            "--sort-by-env", "both",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'Environment               non-prod   prod\nOS Name\nMicrosoft Windows              399   6881\nMicrosoft Windows Server      3614  10118\nRed Hat Enterprise Linux       437    713\nSUSE Linux Enterprise          644   1347')

    def test_main_output_all_envs(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-supported-os",
            "--sort-by-env", "all",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'OS Name\nMicrosoft Windows Server    13732\nMicrosoft Windows            7280\nSUSE Linux Enterprise        1991\nRed Hat Enterprise Linux     1150')

    def test_main_output_non_prod_env(self):
        self.run_test_with_args([
            "--file", "machine_reports/tests/files/Test_Inventory_VMs.xlsx",
            "--get-supported-os",
            "--sort-by-env", "non-prod",
            "--prod-env-labels", "Prod-DC2,Prod-DC1"
        ], 'OS Name\nMicrosoft Windows Server    3614\nSUSE Linux Enterprise        644\nRed Hat Enterprise Linux     437\nMicrosoft Windows            399')

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