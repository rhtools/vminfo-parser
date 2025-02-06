import io
import sys
import typing as t
import weakref

import pandas as pd
from tabulate import tabulate


class CLIOutput:
    def __init__(self: t.Self) -> None:
        # Output buffer to store output.
        self.output = io.StringIO(initial_value="\n\n", newline="\n")

        # Finalizer for flushing buffer to stdout.
        # Will be called when self is deleted or when the interpreter exits
        self._finalize = weakref.finalize(self, self.flush_output, self.output)

        # might need to track the state of this object to ensure it's closed or not
        self._closed = False

    @staticmethod
    def flush_output(output: io.StringIO, file: io.TextIOBase | None = None) -> None:
        """Write StringIO Buffer to file (or stdout).  Closes output buffer.

        Args:
            output (io.StringIO): StringIO obj containing output buffer
            file (io.TextIOBase | None, optional): File to write butter to. Defaults to stdout.
        """
        if output.closed:
            return
        # Delay setting referece to stdout so tests can capture it
        if file is None:
            file = sys.stdout
        file.write(output.getvalue())
        output.close()

    def writeline(self: t.Self, line: t.Any = "") -> None:
        """write string to output buffer.  Adds newline if line does not end with one.

        Args:
            line (str, optional): string to write to output buffer. Defaults to "".
        """
        if self._closed:
            raise ValueError("CLIOutput is already closed")
        if not isinstance(line, str):
            line: str = str(line)
        if not line.endswith("\n"):
            line = line + "\n"
        self.write(line)

    def write(self: t.Self, line: t.Any) -> None:
        """Write string to output buffer.

        Args:
            line (str): string to write to output buffer
        """
        if self._closed:
            raise ValueError("CLIOutput is already closed")
        if not isinstance(line, str):
            line: str = str(line)
        self.output.write(line)

    def close(self: t.Self) -> None:
        """Calls private finalizer for output buffer.  Finalizer will be closed and cannot be called again."""
        if not self._closed:
            self._finalize()
            self._closed = True

    def format_dataframe_output(self: t.Self, dataFrame: pd.DataFrame, os_name: str | None = None) -> None:
        if dataFrame.index.nlevels == 2:
            pass
        else:
            os_version = dataFrame["OS Version"].values
            count = dataFrame["Count"].values
            if count.size > 0:
                self.writeline("")
                self.writeline(os_name)
                self.writeline("--------------")
                self.writeline("OS Version\t\t\t Count")

                for version, count_value in zip(os_version, count):
                    self.writeline(f"{version.ljust(32)} {count_value}")

    def format_series_output(
        self: t.Self, counts: pd.Series, headers: list = "keys", table_format: str = "simple"
    ) -> None:
        df = pd.DataFrame(counts)
        table = tabulate(df, headers=headers, tablefmt=table_format)
        self.writeline(table)

    def print_formatted_disk_space(
        self: t.Self,
        dataFrame: pd.DataFrame,
        os_filter: str | None = None,
    ) -> None:
        """
        Print the formatted disk space information to the output.
        This function displays a header and the formatted data, optionally filtered by the operating system.

        Args:
            dataFrame (pd.DataFrame): A pandas DataFrame, likely sorted by disk space range but not necessarily
            os_filter (Optional[str]): An optional filter to display specific operating system information.

        Returns:
            None
        """
        self.writeline()
        # It looks inconsistent when using the OS version without making everything left justified
        # because sometimes the version is considered a string and sometimes its a num
        # so if OS Version is the name of  the index set the alignment
        if "OS Version" in dataFrame.index.name:
            table = tabulate(dataFrame, headers="keys", colalign=("left", "left", "center"))
        else:
            table = tabulate(dataFrame, headers="keys", numalign="center")
        if os_filter:
            self.writeline(os_filter)
            separator = "=" * len(os_filter)
            self.writeline(separator)
        self.writeline(table)
        self.writeline()

    def print_site_usage(self: t.Self, resource_list: list, dataFrame: pd.DataFrame) -> None:
        """
        Prints the site-wide usage of a specified resource, including Memory, CPU, Disk, or VM count.


        Args:
            resource_list (list): The type of resource to summarize. Options include "Memory", "CPU", "Disk", or "VM".
            dataFrame (pd.DataFrame): A DataFrame containing the relevant data for the site, including
                                      resource usage metrics.

        Returns:
            None: This function does not return a value; it prints the usage information directly to the console.
        """
        dataFrame = dataFrame.set_index("Site Name")
        self.writeline()
        for resource in resource_list:
            if not dataFrame.empty:
                match resource:
                    case "CPU":
                        cpu_usage = dataFrame["Site_CPU_Usage"].astype(int)
                        self.writeline(self.create_site_table(cpu_usage, ["Site Name", "Core Count"]))
                    case "Memory":
                        memory_usage = dataFrame["Site_RAM_Usage"].round(0).astype(int)
                        self.writeline(self.create_site_table(memory_usage, ["Site Name", "Memory Capacity (GB)"]))
                    case "Disk":
                        disk_usage = dataFrame["Site_Disk_Usage"]
                        self.writeline(self.create_site_table(disk_usage, ["Site Name", "Disk Capacity (TB)"]))
                    case "VM":
                        vm_count = dataFrame["Site_VM_Count"]
                        self.writeline(self.create_site_table(vm_count, ["Site Name", "VM Count"]))
                    case _:
                        self.writeline("No data available for the specified resource.")
            else:
                self.writeline("No data available for the specified resource.")
            self.writeline("")

    def create_site_table(self: t.Self, df: pd.DataFrame, headers: list, table_format: str = "simple") -> str:
        """Generate a formatted table from site data.

        This function takes a DataFrame containing site information and converts it into a
        string representation of a table with specified headers. The table is formatted for
        better readability.

        Args:
            df (pd.DataFrame): A DataFrame containing site data.
            headers (list): A list of headers for the table.

        Returns:
            str: A string representation of the formatted table.

        Examples:
            >>> df = pd.DataFrame({'Site A': [1], 'Site B': [2]})
            >>> create_site_table(df, ['Site', 'Value'])
            '  Site    Value\n-------  ------\nSite A      1\nSite B      2'
        """
        table_data = [[site, f"{value}"] for site, value in df.items()]
        return tabulate(table_data, headers=headers, numalign="center", tablefmt=table_format)
