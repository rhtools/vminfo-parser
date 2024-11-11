TESTFILE_SHAPE = (55074, 7)
TESTFILE_DIR = "files"
TESTOUTPUT_DIR = "outputs"
DEFAULT_TESTFILE_NAME = "Test_Inventory_VMs.{}"

SERVER_NAME_MATCHES = {
    "CentOS 4/5 (64-bit)": {"OS_Name": "CentOS", "OS_Version": "4/5 ", "Architecture": "64-bit"},
    "CentOS 4/5/6 (32-bit)": {"OS_Name": "CentOS", "OS_Version": "4/5/6 ", "Architecture": "32-bit"},
    "CentOS 4/5/6 (64-bit)": {"OS_Name": "CentOS", "OS_Version": "4/5/6 ", "Architecture": "64-bit"},
    "CentOS 4/5/6/7 (64-bit)": {"OS_Name": "CentOS", "OS_Version": "4/5/6/7 ", "Architecture": "64-bit"},
    "CentOS 6 (64-bit)": {"OS_Name": "CentOS", "OS_Version": "6 ", "Architecture": "64-bit"},
    "CentOS 7 (64-bit)": {"OS_Name": "CentOS", "OS_Version": "7 ", "Architecture": "64-bit"},
    "Debian GNU/Linux 5 (64-bit)": {"OS_Name": "Debian GNU/Linux", "OS_Version": "5 ", "Architecture": "64-bit"},
    "Debian GNU/Linux 8 (64-bit)": {"OS_Name": "Debian GNU/Linux", "OS_Version": "8 ", "Architecture": "64-bit"},
    "Debian GNU/Linux 9 (64-bit)": {"OS_Name": "Debian GNU/Linux", "OS_Version": "9 ", "Architecture": "64-bit"},
    "FreeBSD 13 or later versions (64-bit)": {
        "OS_Name": "FreeBSD 13 or later versions",
        "OS_Version": None,
        "Architecture": "64-bit",
    },
    "FreeBSD Pre-11 versions (64-bit)": {
        "OS_Name": "FreeBSD Pre-11 versions",
        "OS_Version": None,
        "Architecture": "64-bit",
    },
    "Linux 4.18.0-477.27.2.el8_8.x86_64 AlmaLinux 8.8 (Sapphire Caracal) 8.8 AlmaLinux 8.8 (Sapphire Caracal) cpe:/o:almalinux:almalinux:8::baseos": None,  # noqa
    "Linux 6.1.11 Other Linux 6.x and later kernel": None,
    "Oracle Linux 4/5 (64-bit)": {"OS_Name": "Oracle Linux", "OS_Version": "4/5 ", "Architecture": "64-bit"},
    "Oracle Linux 4/5/6 (64-bit)": {"OS_Name": "Oracle Linux", "OS_Version": "4/5/6 ", "Architecture": "64-bit"},
    "Oracle Linux 4/5/6/7 (64-bit)": {"OS_Name": "Oracle Linux", "OS_Version": "4/5/6/7 ", "Architecture": "64-bit"},
    "Oracle Linux 6 (64-bit)": {"OS_Name": "Oracle Linux", "OS_Version": "6 ", "Architecture": "64-bit"},
    "Oracle Linux 7 (64-bit)": {"OS_Name": "Oracle Linux", "OS_Version": "7 ", "Architecture": "64-bit"},
    "Oracle Linux 8 (64-bit)": {"OS_Name": "Oracle Linux", "OS_Version": "8 ", "Architecture": "64-bit"},
    "Other (32-bit)": {"OS_Name": "Other", "OS_Version": None, "Architecture": "32-bit"},
    "Other (64-bit)": {"OS_Name": "Other", "OS_Version": None, "Architecture": "64-bit"},
    "Other 2.6.x Linux (32-bit)": {"OS_Name": "Other 2.6.x Linux", "OS_Version": None, "Architecture": "32-bit"},
    "Other 2.6.x Linux (64-bit)": {"OS_Name": "Other 2.6.x Linux", "OS_Version": None, "Architecture": "64-bit"},
    "Other 3.x Linux (64-bit)": {"OS_Name": "Other 3.x Linux", "OS_Version": None, "Architecture": "64-bit"},
    "Other 3.x or later Linux (64-bit)": {
        "OS_Name": "Other 3.x or later Linux",
        "OS_Version": None,
        "Architecture": "64-bit",
    },
    "Other 4.x or later Linux (64-bit)": {
        "OS_Name": "Other 4.x or later Linux",
        "OS_Version": None,
        "Architecture": "64-bit",
    },
    "Other 5.x or later Linux (64-bit)": {
        "OS_Name": "Other 5.x or later Linux",
        "OS_Version": None,
        "Architecture": "64-bit",
    },
    "Other Linux (64-bit)": {"OS_Name": "Other Linux", "OS_Version": None, "Architecture": "64-bit"},
    "Red Hat Enterprise Linux 5 (32-bit)": {
        "OS_Name": "Red Hat Enterprise Linux",
        "OS_Version": "5 ",
        "Architecture": "32-bit",
    },
    "Red Hat Enterprise Linux 5 (64-bit)": {
        "OS_Name": "Red Hat Enterprise Linux",
        "OS_Version": "5 ",
        "Architecture": "64-bit",
    },
    "Red Hat Enterprise Linux 6 (64-bit)": {
        "OS_Name": "Red Hat Enterprise Linux",
        "OS_Version": "6 ",
        "Architecture": "64-bit",
    },
    "Red Hat Enterprise Linux 7 (64-bit)": {
        "OS_Name": "Red Hat Enterprise Linux",
        "OS_Version": "7 ",
        "Architecture": "64-bit",
    },
    "Red Hat Enterprise Linux 8 (64-bit)": {
        "OS_Name": "Red Hat Enterprise Linux",
        "OS_Version": "8 ",
        "Architecture": "64-bit",
    },
    "Red Hat Enterprise Linux 9 (64-bit)": {
        "OS_Name": "Red Hat Enterprise Linux",
        "OS_Version": "9 ",
        "Architecture": "64-bit",
    },
    "SUSE Linux Enterprise 10 (64-bit)": {
        "OS_Name": "SUSE Linux Enterprise",
        "OS_Version": "10 ",
        "Architecture": "64-bit",
    },
    "SUSE Linux Enterprise 11 (64-bit)": {
        "OS_Name": "SUSE Linux Enterprise",
        "OS_Version": "11 ",
        "Architecture": "64-bit",
    },
    "SUSE Linux Enterprise 12 (64-bit)": {
        "OS_Name": "SUSE Linux Enterprise",
        "OS_Version": "12 ",
        "Architecture": "64-bit",
    },
    "SUSE Linux Enterprise 15 (64-bit)": {
        "OS_Name": "SUSE Linux Enterprise",
        "OS_Version": "15 ",
        "Architecture": "64-bit",
    },
    "SUSE Linux Enterprise 8/9 (64-bit)": {
        "OS_Name": "SUSE Linux Enterprise",
        "OS_Version": "8/9 ",
        "Architecture": "64-bit",
    },
    "SUSE openSUSE (64-bit)": {"OS_Name": "SUSE openSUSE", "OS_Version": None, "Architecture": "64-bit"},
    "Ubuntu Linux (32-bit)": {"OS_Name": "Ubuntu Linux", "OS_Version": None, "Architecture": "32-bit"},
    "Ubuntu Linux (64-bit)": {"OS_Name": "Ubuntu Linux", "OS_Version": None, "Architecture": "64-bit"},
    "VM OS": None,
    "VMware ESXi 6.x": None,
    "VMware Photon OS (64-bit) ": {"OS_Name": "VMware Photon OS", "OS_Version": None, "Architecture": "64-bit"},
    "Microsoft Windows 10 (64-bit)": {"OS_Name": "Microsoft Windows", "OS_Version": "10", "Architecture": "64-bit"},
    "Microsoft Windows 2000 Professional": None,
    "Microsoft Windows 7 (32-bit)": {"OS_Name": "Microsoft Windows", "OS_Version": "7", "Architecture": "32-bit"},
    "Microsoft Windows 7 (64-bit)": {"OS_Name": "Microsoft Windows", "OS_Version": "7", "Architecture": "64-bit"},
    "Microsoft Windows Server 2003 (32-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2003",
        "Architecture": "32-bit",
    },
    "Microsoft Windows Server 2003 Standard (32-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2003",
        "Architecture": None,
    },
    "Microsoft Windows Server 2008 (32-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2008",
        "Architecture": "32-bit",
    },
    "Microsoft Windows Server 2008 (64-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2008",
        "Architecture": "64-bit",
    },
    "Microsoft Windows Server 2008 R2 (64-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2008 R2",
        "Architecture": "64-bit",
    },
    "Microsoft Windows Server 2012 (64-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2012",
        "Architecture": "64-bit",
    },
    "Microsoft Windows Server 2016 (64-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2016",
        "Architecture": "64-bit",
    },
    "Microsoft Windows Server 2016 or later (64-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2016",
        "Architecture": None,
    },
    "Microsoft Windows Server 2019 (64-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2019",
        "Architecture": "64-bit",
    },
    "Microsoft Windows Server 2022 (64-bit)": {
        "OS_Name": "Microsoft Windows Server",
        "OS_Version": "2022",
        "Architecture": "64-bit",
    },
    "Microsoft Windows Vista (32-bit)": {
        "OS_Name": "Microsoft Windows",
        "OS_Version": "Vista",
        "Architecture": "32-bit",
    },
    "Microsoft Windows XP Professional (32-bit)": {
        "OS_Name": "Microsoft Windows",
        "OS_Version": "XP Professional",
        "Architecture": "32-bit",
    },
}

CLI_OPTIONS = {
    "default": {},
    "disk_space_range_both_env": {
        "get-disk-space-ranges": True,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "both",
    },
    "disk_space_range_prod_env": {
        "get-disk-space-ranges": True,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "prod",
    },
    "disk_space_range_prod_env_by_terabyte": {
        "breakdown-by-terabyte": True,
        "get-disk-space-ranges": True,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "prod",
    },
    "os_min_counts": {
        "get-os-counts": True,
        "minimum-count": 500,
    },
    "supported_os_all_envs": {
        "get-supported-os": True,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "all",
    },
    "supported_os_both_envs": {
        "get-supported-os": True,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "both",
    },
    "supported_os_min_count": {
        "get-supported-os": True,
        "minimum-count": 500,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "all",
    },
    "supported_os_non_prod": {
        "get-supported-os": True,
        "minimum-count": 500,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "non-prod",
    },
    "unsupported_os_both": {
        "get-unsupported-os": True,
        "minimum-count": 500,
        "prod-env-labels": "Prod-DC2,Prod-DC1",
        "sort-by-env": "both",
    },
    "disk_space_by_os": {
        "show-disk-space-by-os": True,
    },
    "granular_disk_space_by_os": {
        "show-disk-space-by-os": True,
        "disk-space-by-granular-os": True,
    },
    # "granular_disk_space_by_os_and_env": {
    #     "show-disk-space-by-os": True,
    #     "disk-space-by-granular-os": True,
    #     "prod-env-labels": "Prod-DC2,Prod-DC1",
    #     "sort-by-env": "both",
    # },
    "output_os_by_version": {
        "output-os-by-version": True,
    },
    "disk_space_ranges": {
        "get-disk-space-ranges": True,
    },
}

EXPECTED_CLI_OUTPUT = {
    "disk_space_range_both_env": (
        "Disk Space Range     non-prod    prod\n"
        "------------------  ----------  ------\n"
        "0 - 200 GB             2312      5082\n"
        "201 - 400 GB           6176     12970\n"
        "401 - 600 GB           3338      5232\n"
        "601 - 800 GB           1588      5534\n"
        "801 GB - 1 TB          396       2793\n"
        "1 - 2 TB               1135      2629\n"
        "2 - 3 TB               1398      915\n"
        "3 - 5 TB               338       821\n"
        "5 - 10 TB              147       1055\n"
        "10 - 20 TB              21       516\n"
        "20 - 50 TB              27       125\n"
        "50 - 100 TB             1         15\n"
        "100 - 114.3 TB          0         2"
    ),
    "disk_space_range_prod_env": (
        "Disk Space Range     prod\n"
        "------------------  ------\n"
        "0 - 200 GB           5082\n"
        "201 - 400 GB        12970\n"
        "401 - 600 GB         5232\n"
        "601 - 800 GB         5534\n"
        "801 GB - 1 TB        2793\n"
        "1 - 2 TB             2629\n"
        "2 - 3 TB             915\n"
        "3 - 5 TB             821\n"
        "5 - 10 TB            1055\n"
        "10 - 20 TB           516\n"
        "20 - 50 TB           125\n"
        "50 - 100 TB           15\n"
        "100 - 114.3 TB        2"
    ),
    "disk_space_range_prod_env_by_terabyte": (
        "Disk Space Range     prod\n"
        "------------------  ------\n"
        "0 - 2 TB            34621\n"
        "2 - 10 TB            2854\n"
        "10 - 20 TB           516\n"
        "20 - 50 TB           125\n"
        "50 - 100 TB           15\n"
        "100 - 114.3 TB        2"
    ),
    "os_min_counts": (
        "OS Name\n"
        "Ubuntu Linux                16583\n"
        "Microsoft Windows Server    13732\n"
        "Oracle Linux                10589\n"
        "Microsoft Windows            7280\n"
        "SUSE Linux Enterprise        1991\n"
        "Red Hat Enterprise Linux     1150\n"
        "CentOS                        592\n"
        "Other                         676"
    ),
    "supported_os_all_envs": (
        "OS Name\n"
        "Microsoft Windows Server    13732\n"
        "Microsoft Windows            7280\n"
        "SUSE Linux Enterprise        1991\n"
        "Red Hat Enterprise Linux     1150"
    ),
    "supported_os_both_envs": (
        "Environment               non-prod   prod\n"
        "OS Name\n"
        "Microsoft Windows Server      3614  10118\n"
        "Microsoft Windows              399   6881\n"
        "SUSE Linux Enterprise          644   1347\n"
        "Red Hat Enterprise Linux       437    713"
    ),
    "supported_os_min_count": (
        "OS Name\n"
        "Microsoft Windows Server    13732\n"
        "Microsoft Windows            7280\n"
        "SUSE Linux Enterprise        1991\n"
        "Red Hat Enterprise Linux     1150"
    ),
    "supported_os_non_prod": (
        "OS Name\n"
        "Microsoft Windows Server    3614\n"
        "SUSE Linux Enterprise        644\n"
        "Other                        836"
    ),
    "unsupported_os_both": (
        "Environment   non-prod  prod\n"
        "OS Name\n"
        "Ubuntu Linux      7041  9542\n"
        "Oracle Linux      3692  6897\n"
        "CentOS             138   454\n"
        "Other               67   609"
    ),
    "disk_space_by_os": (
        "CentOS\n"
        "======\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            278\n"
        "201 - 400 GB          60\n"
        "401 - 600 GB          69\n"
        "601 - 800 GB          26\n"
        "801 GB - 1 TB         56\n"
        "1 - 2 TB              60\n"
        "2 - 3 TB              18\n"
        "3 - 5 TB               9\n"
        "5 - 10 TB              3\n"
        "10 - 20 TB             2\n"
        "20 - 36.3 TB           2\n"
        "\n"
        "\n"
        "Debian GNU/Linux\n"
        "================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            15\n"
        "601 - 800 GB           1\n"
        "\n"
        "\n"
        "Microsoft Windows\n"
        "=================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            508\n"
        "201 - 400 GB         2773\n"
        "401 - 600 GB          198\n"
        "601 - 800 GB         1748\n"
        "801 GB - 1 TB        1228\n"
        "1 - 2 TB              328\n"
        "2 - 3 TB              76\n"
        "3 - 5 TB              108\n"
        "\n"
        "\n"
        "Microsoft Windows Server\n"
        "========================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB           2805\n"
        "201 - 400 GB         4473\n"
        "401 - 600 GB         2211\n"
        "601 - 800 GB         1226\n"
        "801 GB - 1 TB         490\n"
        "1 - 2 TB             1074\n"
        "2 - 3 TB              415\n"
        "3 - 5 TB              410\n"
        "5 - 10 TB             318\n"
        "10 - 20 TB            181\n"
        "20 - 50 TB            93\n"
        "50 - 100 TB           14\n"
        "100 - 114.3 TB         2\n"
        "\n"
        "\n"
        "Oracle Linux\n"
        "============\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB           1513\n"
        "201 - 400 GB         5240\n"
        "401 - 600 GB         1424\n"
        "601 - 800 GB          486\n"
        "801 GB - 1 TB         189\n"
        "1 - 2 TB              641\n"
        "2 - 3 TB              224\n"
        "3 - 5 TB              94\n"
        "5 - 10 TB             492\n"
        "10 - 20 TB            199\n"
        "20 - 35.3 TB          16\n"
        "\n"
        "\n"
        "Other\n"
        "=====\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            23\n"
        "201 - 400 GB           8\n"
        "401 - 600 GB           4\n"
        "1 - 2 TB               1\n"
        "20 - 22.3 TB           1\n"
        "\n"
        "\n"
        "Other 2.6.x Linux\n"
        "=================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            330\n"
        "201 - 400 GB           1\n"
        "401 - 600 GB           1\n"
        "\n"
        "\n"
        "Other 5.x or later Linux\n"
        "========================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "201 - 400 GB           2\n"
        "1 - 2 TB               2\n"
        "\n"
        "\n"
        "Red Hat Enterprise Linux\n"
        "========================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            39\n"
        "201 - 400 GB          631\n"
        "401 - 600 GB          132\n"
        "601 - 800 GB          62\n"
        "801 GB - 1 TB         40\n"
        "1 - 2 TB              128\n"
        "2 - 3 TB              14\n"
        "3 - 5 TB              34\n"
        "5 - 10 TB             59\n"
        "10 - 15.8 TB           5\n"
        "\n"
        "\n"
        "SUSE Linux Enterprise\n"
        "=====================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            620\n"
        "201 - 400 GB          758\n"
        "401 - 600 GB          315\n"
        "601 - 800 GB          114\n"
        "801 GB - 1 TB         43\n"
        "1 - 2 TB              66\n"
        "2 - 3 TB               5\n"
        "3 - 5 TB              52\n"
        "5 - 10 TB              3\n"
        "10 - 20 TB             2\n"
        "\n"
        "\n"
        "Ubuntu Linux\n"
        "============\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            381\n"
        "201 - 400 GB         4514\n"
        "401 - 600 GB         3978\n"
        "601 - 800 GB         3164\n"
        "801 GB - 1 TB        1019\n"
        "1 - 2 TB             1271\n"
        "2 - 3 TB             1361\n"
        "3 - 5 TB              368\n"
        "5 - 10 TB             306\n"
        "10 - 20 TB            138\n"
        "20 - 50 TB            33\n"
        "\n"
        "\n"
        "VMware ESXi 6.x\n"
        "===============\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "401 - 600 GB           1\n"
        "\n"
        "\n"
        "VMware Photon OS\n"
        "================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            47\n"
        "201 - 400 GB          22\n"
        "401 - 600 GB           7\n"
        "601 - 800 GB          11\n"
        "801 GB - 1 TB          8\n"
        "1 - 2 TB              20\n"
        "2 - 3 TB              44\n"
        "3 - 5 TB              15\n"
        "5 - 9.4 TB             4\n"
        "\n"
        "\n"
        "FreeBSD 13 or later versions\n"
        "============================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            10\n"
        "\n"
        "\n"
        "FreeBSD Pre-11 versions\n"
        "=======================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "2 - 3 TB               1\n"
        "\n"
        "\n"
        "Linux 4.18.0-477.27.2.el8_8.x86_64 AlmaLinux 8.8 (Sapphire Caracal) 8.8 AlmaLinux 8.8 (Sapphire Caracal) cpe:/o:almalinux:almalinux:8::baseos\n"
        "=============================================================================================================================================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB             1\n"
        "\n"
        "\n"
        "Linux 6.1.11 Other Linux 6.x and later kernel\n"
        "=============================================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "201 - 400 GB           1\n"
        "\n"
        "\n"
        "Microsoft Windows 2000 Professional\n"
        "===================================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB             2\n"
        "\n"
        "\n"
        "Other 3.x Linux\n"
        "===============\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB            24\n"
        "201 - 400 GB           6\n"
        "401 - 600 GB           1\n"
        "601 - 800 GB           1\n"
        "801 GB - 1 TB          1\n"
        "1 - 2 TB               3\n"
        "2 - 3 TB               2\n"
        "\n"
        "\n"
        "Other 3.x or later Linux\n"
        "========================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "201 - 400 GB           2\n"
        "1 - 2 TB               2\n"
        "\n"
        "\n"
        "Other 4.x or later Linux\n"
        "========================\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "201 - 400 GB          15\n"
        "401 - 600 GB           3\n"
        "601 - 800 GB           5\n"
        "801 GB - 1 TB          3\n"
        "\n"
        "\n"
        "Other Linux\n"
        "===========\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB             6\n"
        "401 - 600 GB           4\n"
        "601 - 800 GB           1\n"
        "1 - 2 TB               1\n"
        "\n"
        "\n"
        "SUSE openSUSE\n"
        "=============\n"
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB             3\n"
        "201 - 400 GB           3\n"
        "1 - 2 TB               3"
    ),
    "granular_disk_space_by_os": (
        "CentOS\n"
        "======\n"
        "OS Version    Disk Space Range     Count\n"
        "------------  ------------------  -------\n"
        "4/5           0 - 200 GB            50\n"
        "4/5           201 - 400 GB          29\n"
        "4/5           401 - 600 GB           2\n"
        "4/5           801 GB - 1 TB         13\n"
        "4/5           1 - 2 TB               7\n"
        "4/5           2 - 3 TB              12\n"
        "4/5           3 - 5 TB               2\n"
        "4/5           5 - 10 TB              2\n"
        "4/5/6         0 - 200 GB            88\n"
        "4/5/6         201 - 400 GB           7\n"
        "4/5/6         401 - 600 GB          15\n"
        "4/5/6         601 - 800 GB           5\n"
        "4/5/6         801 GB - 1 TB          3\n"
        "4/5/6         1 - 2 TB               4\n"
        "4/5/6/7       0 - 200 GB             3\n"
        "4/5/6/7       201 - 400 GB           1\n"
        "4/5/6/7       1 - 2 TB               2\n"
        "6             0 - 200 GB             1\n"
        "6             801 GB - 1 TB          2\n"
        "6             3 - 5 TB               2\n"
        "7             0 - 200 GB            136\n"
        "7             201 - 400 GB          23\n"
        "7             401 - 600 GB          52\n"
        "7             601 - 800 GB          21\n"
        "7             801 GB - 1 TB         38\n"
        "7             1 - 2 TB              47\n"
        "7             2 - 3 TB               6\n"
        "7             3 - 5 TB               5\n"
        "7             5 - 10 TB              1\n"
        "7             10 - 20 TB             2\n"
        "7             20 - 36.3 TB           2\n"
        "\n"
        "\n"
        "Debian GNU/Linux\n"
        "================\n"
        "OS Version    Disk Space Range     Count\n"
        "------------  ------------------  -------\n"
        "5             0 - 200 GB             1\n"
        "9             0 - 200 GB            14\n"
        "9             601 - 800 GB           1\n"
        "\n"
        "\n"
        "Microsoft Windows\n"
        "=================\n"
        "OS Version       Disk Space Range     Count\n"
        "---------------  ------------------  -------\n"
        "10               0 - 200 GB            465\n"
        "10               201 - 400 GB         2763\n"
        "10               401 - 600 GB          196\n"
        "10               601 - 800 GB         1746\n"
        "10               801 GB - 1 TB        1227\n"
        "10               1 - 2 TB              328\n"
        "10               2 - 3 TB              76\n"
        "10               3 - 5 TB              105\n"
        "7                0 - 200 GB            35\n"
        "7                201 - 400 GB          10\n"
        "7                401 - 600 GB           1\n"
        "7                601 - 800 GB           2\n"
        "7                801 GB - 1 TB          1\n"
        "7                3 - 5 TB               3\n"
        "Vista            0 - 200 GB             1\n"
        "XP Professional  0 - 200 GB             7\n"
        "XP Professional  401 - 600 GB           1\n"
        "\n"
        "\n"
        "Microsoft Windows Server\n"
        "========================\n"
        "OS Version    Disk Space Range     Count\n"
        "------------  ------------------  -------\n"
        "2003          0 - 200 GB             8\n"
        "2003          201 - 400 GB           1\n"
        "2003          601 - 800 GB           2\n"
        "2003          1 - 2 TB               1\n"
        "2003          2 - 3 TB               1\n"
        "2008          0 - 200 GB            57\n"
        "2008          201 - 400 GB          10\n"
        "2008          401 - 600 GB          10\n"
        "2008          601 - 800 GB           3\n"
        "2008          801 GB - 1 TB          3\n"
        "2008          1 - 2 TB              11\n"
        "2008          2 - 3 TB               4\n"
        "2008          3 - 5 TB               3\n"
        "2008          10 - 20 TB             2\n"
        "2008 R2       0 - 200 GB            51\n"
        "2008 R2       201 - 400 GB           9\n"
        "2008 R2       401 - 600 GB           2\n"
        "2008 R2       601 - 800 GB           5\n"
        "2008 R2       801 GB - 1 TB          5\n"
        "2008 R2       1 - 2 TB              13\n"
        "2008 R2       2 - 3 TB               6\n"
        "2008 R2       3 - 5 TB              13\n"
        "2008 R2       5 - 10 TB             14\n"
        "2008 R2       10 - 20 TB             6\n"
        "2008 R2       20 - 50 TB             2\n"
        "2012          0 - 200 GB            280\n"
        "2012          201 - 400 GB          252\n"
        "2012          401 - 600 GB          92\n"
        "2012          601 - 800 GB          56\n"
        "2012          801 GB - 1 TB         33\n"
        "2012          1 - 2 TB              50\n"
        "2012          2 - 3 TB              10\n"
        "2012          3 - 5 TB              11\n"
        "2012          5 - 10 TB              3\n"
        "2012          10 - 20 TB             2\n"
        "2016          0 - 200 GB            803\n"
        "2016          201 - 400 GB          942\n"
        "2016          401 - 600 GB          414\n"
        "2016          601 - 800 GB          268\n"
        "2016          801 GB - 1 TB         51\n"
        "2016          1 - 2 TB              234\n"
        "2016          2 - 3 TB              69\n"
        "2016          3 - 5 TB              94\n"
        "2016          5 - 10 TB             78\n"
        "2016          10 - 20 TB            25\n"
        "2016          20 - 50 TB             5\n"
        "2019          0 - 200 GB           1073\n"
        "2019          201 - 400 GB         2377\n"
        "2019          401 - 600 GB         1309\n"
        "2019          601 - 800 GB          698\n"
        "2019          801 GB - 1 TB         279\n"
        "2019          1 - 2 TB              630\n"
        "2019          2 - 3 TB              255\n"
        "2019          3 - 5 TB              239\n"
        "2019          5 - 10 TB             182\n"
        "2019          10 - 20 TB            132\n"
        "2019          20 - 50 TB            69\n"
        "2019          50 - 100 TB            8\n"
        "2019          100 - 114.3 TB         2\n"
        "2022          0 - 200 GB            533\n"
        "2022          201 - 400 GB          882\n"
        "2022          401 - 600 GB          384\n"
        "2022          601 - 800 GB          194\n"
        "2022          801 GB - 1 TB         119\n"
        "2022          1 - 2 TB              135\n"
        "2022          2 - 3 TB              70\n"
        "2022          3 - 5 TB              50\n"
        "2022          5 - 10 TB             41\n"
        "2022          10 - 20 TB            14\n"
        "2022          20 - 50 TB            17\n"
        "2022          50 - 100 TB            6\n"
        "\n"
        "\n"
        "Oracle Linux\n"
        "============\n"
        "OS Version    Disk Space Range     Count\n"
        "------------  ------------------  -------\n"
        "4/5           0 - 200 GB            245\n"
        "4/5           201 - 400 GB          823\n"
        "4/5           401 - 600 GB          360\n"
        "4/5           601 - 800 GB          85\n"
        "4/5           801 GB - 1 TB         32\n"
        "4/5           1 - 2 TB              105\n"
        "4/5           2 - 3 TB              21\n"
        "4/5           10 - 20 TB             1\n"
        "4/5/6         0 - 200 GB             2\n"
        "4/5/6         201 - 400 GB           1\n"
        "4/5/6         401 - 600 GB           1\n"
        "4/5/6/7       0 - 200 GB            15\n"
        "4/5/6/7       201 - 400 GB           8\n"
        "4/5/6/7       601 - 800 GB           2\n"
        "4/5/6/7       1 - 2 TB               9\n"
        "4/5/6/7       5 - 10 TB              1\n"
        "6             0 - 200 GB            71\n"
        "6             201 - 400 GB          121\n"
        "6             401 - 600 GB          30\n"
        "6             601 - 800 GB          24\n"
        "6             801 GB - 1 TB          3\n"
        "6             1 - 2 TB              21\n"
        "6             2 - 3 TB              23\n"
        "6             5 - 10 TB              4\n"
        "6             10 - 20 TB             4\n"
        "7             0 - 200 GB           1179\n"
        "7             201 - 400 GB         4269\n"
        "7             401 - 600 GB          974\n"
        "7             601 - 800 GB          356\n"
        "7             801 GB - 1 TB         146\n"
        "7             1 - 2 TB              485\n"
        "7             2 - 3 TB              180\n"
        "7             3 - 5 TB              94\n"
        "7             5 - 10 TB             487\n"
        "7             10 - 20 TB            194\n"
        "7             20 - 35.3 TB          16\n"
        "8             0 - 200 GB             1\n"
        "8             201 - 400 GB          18\n"
        "8             401 - 600 GB          59\n"
        "8             601 - 800 GB          19\n"
        "8             801 GB - 1 TB          8\n"
        "8             1 - 2 TB              21\n"
        "\n"
        "\n"
        "Red Hat Enterprise Linux\n"
        "========================\n"
        "OS Version    Disk Space Range     Count\n"
        "------------  ------------------  -------\n"
        "5             0 - 200 GB             4\n"
        "5             201 - 400 GB           7\n"
        "5             401 - 600 GB           4\n"
        "5             1 - 2 TB               1\n"
        "5             3 - 5 TB               1\n"
        "6             0 - 200 GB            14\n"
        "6             1 - 2 TB               4\n"
        "6             2 - 3 TB               3\n"
        "7             0 - 200 GB            18\n"
        "7             201 - 400 GB          10\n"
        "7             401 - 600 GB           6\n"
        "7             601 - 800 GB           1\n"
        "7             1 - 2 TB               9\n"
        "7             2 - 3 TB               1\n"
        "7             3 - 5 TB               2\n"
        "7             5 - 10 TB              5\n"
        "8             0 - 200 GB             3\n"
        "8             201 - 400 GB          294\n"
        "8             401 - 600 GB          53\n"
        "8             601 - 800 GB          21\n"
        "8             801 GB - 1 TB         21\n"
        "8             1 - 2 TB              46\n"
        "8             2 - 3 TB              10\n"
        "8             3 - 5 TB              28\n"
        "8             5 - 10 TB             19\n"
        "8             10 - 15.8 TB           5\n"
        "9             201 - 400 GB          320\n"
        "9             401 - 600 GB          69\n"
        "9             601 - 800 GB          40\n"
        "9             801 GB - 1 TB         19\n"
        "9             1 - 2 TB              68\n"
        "9             3 - 5 TB               3\n"
        "9             5 - 10 TB             35\n"
        "\n"
        "\n"
        "SUSE Linux Enterprise\n"
        "=====================\n"
        "OS Version    Disk Space Range     Count\n"
        "------------  ------------------  -------\n"
        "10            201 - 400 GB           1\n"
        "11            0 - 200 GB            55\n"
        "11            201 - 400 GB          137\n"
        "11            401 - 600 GB          95\n"
        "11            601 - 800 GB          33\n"
        "11            801 GB - 1 TB          3\n"
        "11            1 - 2 TB              15\n"
        "11            2 - 3 TB               2\n"
        "11            3 - 5 TB               2\n"
        "12            0 - 200 GB            521\n"
        "12            201 - 400 GB          390\n"
        "12            401 - 600 GB          109\n"
        "12            601 - 800 GB          29\n"
        "12            801 GB - 1 TB         20\n"
        "12            1 - 2 TB              27\n"
        "12            2 - 3 TB               2\n"
        "12            3 - 5 TB               6\n"
        "12            5 - 10 TB              3\n"
        "12            10 - 20 TB             2\n"
        "15            0 - 200 GB            44\n"
        "15            201 - 400 GB          229\n"
        "15            401 - 600 GB          111\n"
        "15            601 - 800 GB          52\n"
        "15            801 GB - 1 TB         20\n"
        "15            1 - 2 TB              24\n"
        "15            2 - 3 TB               1\n"
        "15            3 - 5 TB              44\n"
        "8/9           201 - 400 GB           1"
    ),
    # "granular_disk_space_by_os_and_env": "non-prod    prod",
    "output_os_by_version": (
        "CentOS\n"
        "--------------\n"
        "OS Version			 Count\n"
        "7                                341\n"
        "4/5/6                            122\n"
        "4/5                              118\n"
        "4/5/6/7                          6\n"
        "6                                5\n"
        "\n"
        "Debian GNU/Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "9                                15\n"
        "5                                2\n"
        "8                                1\n"
        "\n"
        "Microsoft Windows\n"
        "--------------\n"
        "OS Version			 Count\n"
        "10                               7219\n"
        "7                                52\n"
        "XP Professional                  8\n"
        "Vista                            1\n"
        "\n"
        "Microsoft Windows Server\n"
        "--------------\n"
        "OS Version			 Count\n"
        "2019                             7264\n"
        "2016                             2991\n"
        "2022                             2446\n"
        "2012                             789\n"
        "2008 R2                          126\n"
        "2008                             103\n"
        "2003                             13\n"
        "\n"
        "Oracle Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "7                                8438\n"
        "4/5                              1680\n"
        "6                                304\n"
        "8                                128\n"
        "4/5/6/7                          35\n"
        "4/5/6                            4\n"
        "\n"
        "Other\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          38\n"
        "\n"
        "Other 2.6.x Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          332\n"
        "\n"
        "Other 5.x or later Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          4\n"
        "\n"
        "Red Hat Enterprise Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "9                                554\n"
        "8                                501\n"
        "7                                55\n"
        "6                                21\n"
        "5                                19\n"
        "\n"
        "SUSE Linux Enterprise\n"
        "--------------\n"
        "OS Version			 Count\n"
        "12                               1112\n"
        "15                               532\n"
        "11                               345\n"
        "10                               1\n"
        "8/9                              1\n"
        "\n"
        "Ubuntu Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          16583\n"
        "\n"
        "VMware ESXi 6.x\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          1\n"
        "\n"
        "VMware Photon OS\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          179\n"
        "\n"
        "FreeBSD 13 or later versions\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          10\n"
        "\n"
        "FreeBSD Pre-11 versions\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          1\n"
        "\n"
        "Linux 4.18.0-477.27.2.el8_8.x86_64 AlmaLinux 8.8 (Sapphire Caracal) 8.8 AlmaLinux 8.8 (Sapphire Caracal) cpe:/o:almalinux:almalinux:8::baseos\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          1\n"
        "\n"
        "Linux 6.1.11 Other Linux 6.x and later kernel\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          1\n"
        "\n"
        "Microsoft Windows 2000 Professional\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          2\n"
        "\n"
        "Other 3.x Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          38\n"
        "\n"
        "Other 3.x or later Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          4\n"
        "\n"
        "Other 4.x or later Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          26\n"
        "\n"
        "Other Linux\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          12\n"
        "\n"
        "SUSE openSUSE\n"
        "--------------\n"
        "OS Version			 Count\n"
        "unknown                          9"
    ),
    "disk_space_ranges": (
        "Disk Space Range     Count\n"
        "------------------  -------\n"
        "0 - 200 GB           7394\n"
        "201 - 400 GB         19146\n"
        "401 - 600 GB         8570\n"
        "601 - 800 GB         7122\n"
        "801 GB - 1 TB        3189\n"
        "1 - 2 TB             3764\n"
        "2 - 3 TB             2313\n"
        "3 - 5 TB             1159\n"
        "5 - 10 TB            1202\n"
        "10 - 20 TB            537\n"
        "20 - 50 TB            152\n"
        "50 - 100 TB           16\n"
        "100 - 114.3 TB         2"
    ),
}

EXPECTED_ARGPARSE_TO_YAML = {
    "breakdown_by_terabyte": False,
    "disk_space_by_granular_os": False,
    "file": "testfile.yaml",
    "generate_graphs": False,
    "get_disk_space_ranges": False,
    "get_os_counts": False,
    "get_supported_os": False,
    "get_unsupported_os": False,
    "minimum_count": 0,
    "os_name": None,
    "output_os_by_version": False,
    "over_under_tb": False,
    "prod_env_labels": None,
    "show_disk_space_by_os": False,
    "sort_by_env": None,
    "sort_by_site": False,
}
TEST_DATAFRAMES = [
    {
        "df": {
            "VM OS": ["Windows 10", "Ubuntu 20.04", "CentOS 7"],
            "Environment": ["Prod", "Dev", "Prod"],
            "VM MEM (GB)": [8, 16, 32],
            "VM Provisioned (GB)": [100, 200, 300],
            "VM CPU": [4, 8, 12],
        },
        "unit": "GB",
        "version": 1,
    },
    {
        "df": {
            "OS according to the configuration file": [
                None,
                None,
                "CentOS 7",
            ],
            "OS according to the VMware Tools": [
                "Windows 10",
                "Ubuntu 20.04",
                None,
            ],
            "ent-env": ["Prod", "Dev", "Prod"],
            "Memory": [8, 16, 32],
            "Total disk capacity MiB": [100, 200, 300],
            "CPUs": [4, 8, 12],
        },
        "unit": "MB",
        "version": 2,
    },
]

MAIN_FUNCTION_CALLS = {
    "sort_by_site": ["vm_data", "cli_output"],
    "show_disk_space_by_os": ["config", "analyzer", "cli_output", "visualizer"],
    "get_disk_space_ranges": ["config", "analyzer", "cli_output", "visualizer"],
    "get_os_counts": ["config", "analyzer", "cli_output", "visualizer"],
    "output_os_by_version": ["analyzer", "cli_output", "visualizer"],
    "get_supported_os": ["config", "analyzer", "cli_output", "visualizer"],
    "get_unsupported_os": ["analyzer", "cli_output", "visualizer"],
}
