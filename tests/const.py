TESTFILE_SHAPE = (55074, 7)


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
    "Linux 4.18.0-477.27.2.el8_8.x86_64 AlmaLinux 8.8 (Sapphire Caracal) 8.8 AlmaLinux 8.8 (Sapphire Caracal) cpe:/o:almalinux:almalinux:8::baseos": None,
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
