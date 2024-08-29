import pytest
import pandas as pd
from ..vm_csv_parser import set_column_headings

@pytest.fixture
def mock_dataframe():
    return pd.DataFrame({
        "VM OS": ["Windows 10", "Ubuntu 20.04", "CentOS 7"],
        "Environment": ["Prod", "Dev", "Prod"],
        "VM MEM (GB)": [8, 16, 32],
        "VM Provisioned (GB)": [100, 200, 300]
    })

@pytest.fixture
def mock_dataframe_v2():
    return pd.DataFrame({
        "OS according to the configuration file": ["Windows 10", "Ubuntu 20.04", "CentOS 7"],
        "ent-env": ["Prod", "Dev", "Prod"],
        "Memory": [8, 16, 32],
        "Total disk capacity MiB": [100, 200, 300]
    })

def test_set_column_headings_version1(mock_dataframe):
    
    column_headings = set_column_headings(mock_dataframe)
    
    assert column_headings == {
        "operatingSystem": "VM OS",
        "environment": "Environment",
        "vmMemory": 'VM MEM (GB)',
        "vmDisk": 'VM Provisioned (GB)',
        "unitType": 'GB'
    }

def test_set_column_headings_version2(mock_dataframe_v2):
    
    column_headings = set_column_headings(mock_dataframe_v2)
    assert column_headings == {
        "operatingSystem": "OS according to the configuration file",
        "environment": "ent-env",
        "vmMemory": 'Memory',
        "vmDisk": 'Total disk capacity MiB',
        "unitType": 'MB'
    }

def test_set_column_headings_invalid_columns():
    invalid_df = pd.DataFrame({"Invalid": [1, 2, 3]})
    with pytest.raises(ValueError):
        set_column_headings(invalid_df)

def test_set_column_headings_empty_dataframe():
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError):
        set_column_headings(empty_df)