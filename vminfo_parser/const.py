from types import MappingProxyType

COLUMN_HEADERS = MappingProxyType(
    {
        "VERSION_1": MappingProxyType(
            {
                "operatingSystem": "VM OS",
                "environment": "Environment",
                "vmMemory": "VM MEM (GB)",
                "vmDisk": "VM Provisioned (GB)",
            }
        ),
        "VERSION_2": MappingProxyType(
            {
                "operatingSystem": "OS according to the configuration file",
                "environment": "ent-env",
                "vmMemory": "Memory",
                "vmDisk": "Total disk capacity MiB",
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
