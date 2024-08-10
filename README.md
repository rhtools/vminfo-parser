# Description

The `vm_csv_parser.py` is intended to take a CSV file and parse it creating both text tables and graphs using `matplotlib` and `pandas`. The primary purpose is to help construct reports around OpenShift Virtualization. As such things like `supported operating systems` and `disk space ranges` are based on the current understanding of both support and difficulty to migrate as of the publishing on this script in July 2024.

**NOTE**: The graphs are not saved to disk currently. That means you must either screenshot or save the resulting graph which will be shown to the screen.

This script is under active development and currently it is assumed the main areas of interest in a CSV file are the Operating System and the disk space used per VM. There is some minor functionality for getting the average amount of ram allocated per VM.

This program expects a CSV with the following headings:
```
VM Power,	VM OS,	VM CPU,	VM MEM (GB), VM Provisioned (GB), VM Used (GB),	Environment	
```

**OR**

```
OS according to the configuration file, ent-env, Memory, Total disk capacity MiB
```

More headings may be supported in the future and are currently parsed in the function called _set_column_headings_.


The `add_extra_columns` funmction will add OS Name, OS Version and Architecture

Sample input:
```
|VM Power	|VM OS		        |VM CPU |VM MEM (GB)|VM Provisioned (GB)|VM Used (GB)|Environment	
|PoweredOn	|CentOS 4/5 (32-bit)|	2   |	2	    | 82.112 	        |25.831	     |Test
```

Currently, the CSV requirements are loosely based on RVTools. However, given the data set this program was developed on, it is currently tightly coupled to the above headings. 

In the future it is planned to support flags which the user can use to indicate what column headings will represent what type of data. This is **not** yet implemented.


Below is the help output:
```
Process some arguments.

options:
  -h, --help            show this help message and exit

Disk Space Analysis:
  Options related to generating disk ranges by os, environment or both

  --get-disk-space-ranges
                        This flag will get disk space ranges regardless of OS. Can be combine with --prod-env-labels and --sort-by-env to target a specific environment
  --show-disk-space-by-os
                        Show disk space by OS
  --breakdown-by-terabyte
                        Breaks disk space down into 0-2TB, 2-9TB and 9TB+ instead of the default categories

Operating System Analysis:
  Options related to generating OS type break downby OS version, environment or both

  --output-os-by-version
                        Output OS by version
  --get-os-counts       Generate a report that counts the inventory broken down by OS
  --os-name OS_NAME     The name of the Operating System to produce a report about
  --minimum-count MINIMUM_COUNT
                        Anything below this number will be excluded from the results
  --get-supported-os    Display a graph of the supported operating systems for OpenShift Virt
  --get-unsupported-os  Display a graph of the unsupported operating systems for OpenShift Virt

Arguments that apply to both OS and Disk:
  --file FILE           The file to parse
  --sort-by-env [SORT_BY_ENV]
                        Sort disk by environment. Use "all" to get combine count, "both" to show both non-prod and prod, or specify one.
  --prod-env-labels [PROD_ENV_LABELS]
                        The values in your data that represent prod environments. This is used to generate prod and non-prod stats. Passed as CSV i.e. --prod-env-labels 'baker,dte'
  --generate-graphs     Choose whether or not to output visual graphs. If this option is not set, a text table will be outputted to the terminal
```


# Examples

Below are examples for both disk and OS related reports

### Generate Disk Range by environment and OS

The following generates a text table to the CLI:
```
./vm_csv_parser.py --file <path_to_file> --sort-by-env both --show-disk-space-by-os --prod-env-labels atlas,herod
```

Output looks similar to (no graphs included):
```

SUSE Linux Enterprise
---------------------------------
Environment                            non-prod   prod       
3-200 GB                               105        112       
201-400 GB                             209        389       
401-600 GB                             501        128       
601-900 GB                             50         100       
901-1500 GB                            14         22        
1501-2000 GB                           4          4         
2001-3000 GB                           1          4         
3001-5000 GB                           11         31        
5001-9000 GB                           1          2         
9001-20399 GB                          0          2        

Ubuntu
---------------------------------
Environment                            non-prod   prod       
0-200 GB                               449        642      
201-400 GB                             269        257      
401-600 GB                             194        252      
601-900 GB                             106        310      
901-1500 GB                            335        364       
1501-2000 GB                           104        135       
2001-3000 GB                           138        131       
3001-5000 GB                           307        152       
5001-9000 GB                           83         113       
9001-71084 GB                          20         176   
```

This is a similar command but limiting the OS to a specific OS and generating a graph

```
./vm_csv_parser.py --file <path_to_file> --show-disk-space-by-os --sort-by-env both --prod-env-labels atlas,herod --generate-graphs --os-name "Microsoft Windows"
```



### Generate Disk Range in TB by environment and OS


```
./vm_csv_parser.py --file <path_to_file> --get-disk-space-ranges --sort-by-env prod --prod-env-labels atlas,herod --breakdown-by-terabyte --generate-graphs
```