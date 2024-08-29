import unittest
import io
import sys
import argparse
from contextlib import redirect_stdout
from ..vm_csv_parser import main

class TestVMCSVParser(unittest.TestCase):

    def test_main_output(self):
        # Create an in-memory text stream
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Define the test arguments

        # Mock the argparse.parse_args method
        def mock_parse_args(args):
            return argparse.Namespace(**{arg.split('=')[0]: arg.split('=')[1] for arg in args})
        
        # Set the mocked parse_args method
        argparse.parse_args = mock_parse_args
        
        try:
            # Run the main function with sample arguments
            main([
            "--file", "/home/stratus/temp/Inventory_VMs_redhat.xlsx",
            "--get-supported-os",
            "--sort-by-env", "all",
            "--prod-env-labels", "prod,prod2"
        ])
            
            # Get the output
            output = captured_output.getvalue().strip()
            
            # Add your assertions here
            self.assertIn('All version 1 columns are present in the DataFrame.\n\nOS Name\nMicrosoft Windows Server    xxx\nMicrosoft Windows            xxx\nSUSE Linux Enterprise        xxx\nRed Hat Enterprise Linux     xxx\nName: count, dtype: int64', output)

        finally:
            # Restore the original parse_args method
            argparse.parse_args = argparse.parse_args
            
if __name__ == '__main__':
    unittest.main()