# vminfo_parser

## Important

`legacy/vm_csv_parser.py` is the original program. However, it was not easy to test of for others to contribute. It is being kept around to ensure like-functionality in the new program `vminfo_parser`. VMInfo is a refactored (into classes) version with tests and a test dataset available for basic output testing.

For more information on the original version, see its [README.md](legacy/README.md)

## Installation

vminfo_parser can be installed with pip, or executed directly from a cloned repo.

### pip

```
pip3 install git+https://github.com/rhtools/vminfo-parser.git

vminfo-parser --help
```

### pip - versioned

```
pip3 install git+https://github.com/rhtools/vminfo-parser.git@v1.0.0

vminfo-parser --help
```

### git repo

```
git clone https://github.com/rhtools/vminfo-parser.git

cd vminfo-parser
pip3 install requirements.txt
python3 -m vminfo_parser --help
```

## Usage

```
[-h] [--file FILE | --yaml YAML] [--sort-by-env [SORT_BY_ENV]] [--sort-by-site] [--prod-env-labels [PROD_ENV_LABELS]] [--generate-graphs]
                   [--get-disk-space-ranges] [--show-disk-space-by-os] [--disk-space-by-granular-os] [--breakdown-by-terabyte] [--over-under-tb]
                   [--output-os-by-version] [--get-os-counts] [--os-name OS_NAME] [--minimum-count MINIMUM_COUNT] [--get-supported-os] [--get-unsupported-os]
                   [--generate-yaml]

Process VM CSV file

options:
  -h, --help            show this help message and exit
  --file FILE           The file to parse
  --yaml YAML           Path to YAML configuration file
  --sort-by-env [SORT_BY_ENV]
                        Sort disk by environment. Use "all" to get combine count, "both" to show both non-prod and prod, or specify one.
  --sort-by-site        Generate per-site stats.
  --prod-env-labels [PROD_ENV_LABELS]
                        The values in your data that represent prod environments. This is used to generate prod and non-prod stats. Passed as CSV i.e. --prod-
                        env-labels 'baker,dte'
  --generate-graphs     Choose whether or not to output visual graphs. If this option is not set, a text table will be outputted to the terminal
  --get-disk-space-ranges
                        This flag will get disk space ranges regardless of OS. Can be combine with --prod-env-labels and --sort-by-env to target a specific
                        environment
  --show-disk-space-by-os
                        Show disk space by OS
  --disk-space-by-granular-os
                        When getting disk space by os, this breaks those results more granularly
  --breakdown-by-terabyte
                        Breaks disk space down into 0-2 TiB, 2-9 TiB and 9 TiB+ instead of the default categories
  --over-under-tb       A simple break down of machines under 1 TiB and those over 1 TiB
  --output-os-by-version
                        Output OS by version
  --get-os-counts       Generate a report that counts the inventory broken down by OS
  --os-name OS_NAME     The name of the Operating System to produce a report about
  --minimum-count MINIMUM_COUNT
                        Anything below this number will be excluded from the results
  --get-supported-os    Display a graph of the supported operating systems for OpenShift Virt
  --get-unsupported-os  Display a graph of the unsupported operating systems for OpenShift Virt
  --generate-yaml       Writes a Yaml file of all the current options available
```

This program can be used either by passing in a combination of flags or by using a YAML file with the options set within.

For convenience, there is a `--generate-yaml` flag which will generate a YAML file with all of the possible arguments set to their default. If you want to capture all of the options that you pass into the program for future usage you can use the program with all of the flags you required and then append `--generate-yaml`.

> [!NOTE]
> If you use the `--generate-yaml` the program will not actually process data, it will simply generate a YAML file with either default or overridden options!

`--yaml` and `--file` are mutually exclusive and only one option should be used. It is assumed that if you are passing in a `--file` that you will want to pass in all the required arguments to the program via flags.

## Examples

### Get OS Counts

```sh
vminfo-parser --file tests/files/Test_Inventory_VMs.csv --get-os-counts --generate-graphs

OS Name
Ubuntu Linux                16583
Microsoft Windows Server    13732
Oracle Linux                10589
Microsoft Windows            7280
SUSE Linux Enterprise        1991
Red Hat Enterprise Linux     1150
CentOS                        592
```

![plot](examples/Get_OS_Counts.png)

### Get Supported OS
```sh
vminfo_parser --file tests/files/Test_Inventory_VMs.csv --generate-graphs  --sort-by-env "all" --prod-env-labels Prod-DC1,Prod-DC2 --get-supported-os     

OS Name
Microsoft Windows Server    13732
Microsoft Windows            7280
SUSE Linux Enterprise        1991
Red Hat Enterprise Linux     1150
```

![plot](examples/Get_Supported_OS.png)

### Get Disk Space Ranges

```sh
vminfo_parser --file tests/files/Test_Inventory_VMs.csv --generate-graphs  --get-disk-space-ranges --sort-by-env "all" --prod-env-labels Prod-DC1,Prod-DC2

Count                                  
Disk Space Range    Count            
0-200 GiB           7519             
201-400 GiB         19361            
401-600 GiB         8619             
601-900 GiB         8584             
901-1500 GiB        4620             
1501-2000 GiB       921              
2001-3000 GiB       2358             
3001-5000 GiB       1176             
5001-9000 GiB       1138             
9001-114256 GiB     773
```

![plot](examples/Get_Disk_Space_Ranges.png)
