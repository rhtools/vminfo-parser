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

### git repo

```
git clone https://github.com/rhtools/vminfo-parser.git

cd vminfo-parser
pip3 install requirements.txt
python3 -m vminfo_parser --help
```

## Usage

```
usage: vminfo_parser [-h] (--file FILE | --yaml YAML) [--sort-by-env [SORT_BY_ENV]]
                     [--prod-env-labels [PROD_ENV_LABELS]] [--generate-graphs]
                     [--get-disk-space-ranges] [--show-disk-space-by-os]
                     [--breakdown-by-terabyte] [--over-under-tb]
                     [--output-os-by-version] [--get-os-counts] [--os-name OS_NAME] 
                     [--minimum-count MINIMUM_COUNT] [--get-supported-os] 
                     [--get-unsupported-os]

Process VM CSV file

options:
  -h, --help            show this help message and exit
  --file FILE           The file to parse
  --yaml YAML           Path to YAML configuration file
  --sort-by-env [SORT_BY_ENV]
                        Sort disk by environment. Use "all" to get combine count,
                        "both" to show both non-prod and prod, or specify one.
  --prod-env-labels [PROD_ENV_LABELS]
                        The values in your data that represent prod environments. 
                        This is used to generate prod and non-prod stats. 
                        Passed as CSV i.e. --prod-env-labels 'baker,dte'
  --generate-graphs     Choose whether or not to output visual graphs. If this option 
                        is not set, a text table will be outputted to the terminal
  --get-disk-space-ranges
                        This flag will get disk space ranges regardless of OS. 
                        Can be combine with --prod-env-labels and --sort-by-env 
                        to target a specific environment
  --show-disk-space-by-os
                        Show disk space by OS
  --breakdown-by-terabyte
                        Breaks disk space down into 0-2TB, 2-9TB and 9TB+ instead 
                        of the default categories
  --over-under-tb       A simple break down of machines under 1TB and those over 1TB
  --output-os-by-version
                        Output OS by version
  --get-os-counts       Generate a report that counts the inventory broken down by OS
  --os-name OS_NAME     The name of the Operating System to produce a report about
  --minimum-count MINIMUM_COUNT
                        Anything below this number will be excluded from the results
  --get-supported-os    Display a graph of the supported operating systems 
                        for OpenShift Virt
  --get-unsupported-os  Display a graph of the unsupported operating systems 
                        for OpenShift Virt 
```

Configurations can also be passed as a yaml based config file using the same option names.

For examle, if the below yaml was in a file named `config.yaml`,

```yaml
file: <filename>
get-supported-os: true
prod-env-labels: Prod-DC2,Prod-DC1
sort-by-env: both
```

the script could be executed as

```sh
vminfo-parse --yaml config.yaml
```

or as

```sh
vminfo-parse --file <filename> --get-supported-os --prod-env-labels "Prod-DC2,Prod-DC1" --sort-by-env "both"
```

and produce the same output.
