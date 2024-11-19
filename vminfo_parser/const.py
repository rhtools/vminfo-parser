from types import MappingProxyType

COLUMN_HEADERS = MappingProxyType(
    {
        "VERSION_1": MappingProxyType(
            {
                "operatingSystemFromVMTools": "VM OS",
                "operatingSystemFromVMConfig": "VM OS",
                "environment": "Environment",
                "vmMemory": "VM MEM (GB)",
                "vmDisk": "VM Provisioned (GB)",
                "vCPU": "VM CPU",
            }
        ),
        "VERSION_2": MappingProxyType(
            {
                "operatingSystemFromVMConfig": "OS according to the configuration file",
                "operatingSystemFromVMTools": "OS according to the VMware Tools",
                "environment": "ent-env",
                "vmMemory": "Memory",
                "vmDisk": "Total disk capacity MiB",
                "vCPU": "CPUs",
            }
        ),
    }
)


MIME = MappingProxyType(
    {
        "excel": frozenset(
            [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.oasis.opendocument.spreadsheet",
                "application/vnd.ms-excel",
            ]
        ),
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "xls": "application/vnd.ms-excel",
        "csv": "text/csv",
    }
)

EXTRA_COLUMNS_DEST = ["OS Name", "OS Version", "Architecture"]

EXTRA_COLUMNS_NON_WINDOWS_REGEX = (
    r"^(?!.*Microsoft)(?P<OS_Name>.*?)(?:\s+"
    r"(?P<OS_Version>\d+(?:/\d+)*\s*(?:or later)?\s*)?\s*"
    r"\((?P<Architecture>.*?64-bit|.*?32-bit)\))"
)

EXTRA_COLUMNS_WINDOWS_SERVER_REGEX = (
    r"^(?P<OS_Name>Microsoft Windows Server)\s+"
    r"(?P<OS_Version>\d+(?:\.\d+)*(?:\s*R\d+)?(?:\s*SP\d+)?)"
    r"(?:\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\))?"
)
EXTRA_COLUMNS_WINDOWS_DESKTOP_REGEX = (
    r"^(?P<OS_Name>Microsoft Windows)\s+(?!Server)"
    r"(?P<OS_Version>XP Professional|\d+(?:\.\d+)*|Vista|7|8|10)\s*"
    r"\((?P<Architecture>.*?64-bit|.*?32-bit)\)"
)

SUPPORTED_OS_COLORS = MappingProxyType(
    {
        "Red Hat Enterprise Linux": "red",
        "SUSE Linux Enterprise": "green",
        "Microsoft Windows Server": "navy",
        "Microsoft Windows": "blue",
    }
)

SUPPORTED_OSES = frozenset(SUPPORTED_OS_COLORS.keys())
