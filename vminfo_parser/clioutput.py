import io
import sys
import typing as t
import weakref

import pandas as pd


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
    def flush_output(output: io.StringIO, file: t.Optional[io.TextIOBase] = None) -> None:
        """Write StringIO Buffer to file (or stdout).  Closes output buffer.

        Args:
            output (io.StringIO): StringIO obj containing output buffer
            file (t.Optional[io.TextIOBase], optional): File to write butter to. Defaults to stdout.
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

    def format_dataframe_output(self: t.Self, dataFrame: pd.DataFrame, os_name: t.Optional[str] = None) -> None:
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

    def print_formatted_disk_space(
        self: t.Self,
        sorted_range_counts_by_environment: pd.DataFrame,
        environment_filter: str,
        env_keywords: list[str],
        os_filter: t.Optional[str] = None,
    ) -> None:
        col_widths = (
            {
                "Environment": 22,
                **{env: 10 for env in sorted_range_counts_by_environment.columns},
            }
            if env_keywords and environment_filter != "all"
            else {**{env: 17 for env in sorted_range_counts_by_environment.columns}}
        )
        formatted_rows = []

        if environment_filter == "all":
            formatted_rows.append("Disk Space Range".ljust(20) + "Count".ljust(col_widths["Count"]))
            justification = 19
        else:
            justification = 15

        for index, row in sorted_range_counts_by_environment.iterrows():
            formatted_row = [str(index).ljust(justification)]
            for col_name, width in col_widths.items():
                value = str(row[col_name]) if col_name in row.index else ""
                formatted_row.append(value.ljust(width))
            formatted_rows.append(" ".join(formatted_row))

        formatted_df_str = "\n".join(formatted_rows)

        temp_heading = ""
        if os_filter:
            self.writeline(os_filter)
            self.writeline("---------------------------------")

        for headings in list(col_widths.keys()):
            if temp_heading:
                temp_heading += headings.ljust(11)
            else:
                temp_heading += headings.ljust(39)
        self.writeline(temp_heading)
        self.writeline(formatted_df_str)
        self.writeline()

    def print_disk_space_ranges(self: t.Self, range_counts: dict[tuple[int, int], int]) -> None:
        self.writeline("Disk Space Range (GB)\t\tCount")
        for disk_range, count in range_counts.items():
            disk_range_str = f"{disk_range[0]}-{disk_range[1]}"
            self.writeline(f"{disk_range_str.ljust(32)} {count}")

    def print_site_usage(self: t.Self, resource_list: list, dataFrame: pd.DataFrame) -> None:
        """
        Prints the site-wide usage of a specified resource, including Memory, CPU, Disk, or VM count.


        Args:
            resource_list (list): The type of resource to summarize. Options include "Memory", "CPU", "Disk", or "VM".
            dataFrame (pd.DataFrame): A DataFrame containing the relevant data for the site, including resource usage metrics.

        Returns:
            None: This function does not return a value; it prints the usage information directly to the console.
        """
        for resource in resource_list:
            self.writeline(f"Site Wide {resource} Usage")
            self.writeline("-------------------")
            if not dataFrame.empty:
                match resource:
                    case "CPU":
                        cpu_usage = dataFrame["Site_CPU_Usage"].astype(int)
                        for index, row in dataFrame.iterrows():
                            self.writeline(f"{row['Site Name']}\t\t{cpu_usage[index]} Cores")
                    case "Memory":
                        memory_usage = dataFrame["Site_RAM_Usage"].round(0).astype(int)
                        for index, row in dataFrame.iterrows():
                            self.writeline(f"{row['Site Name']}\t\t{memory_usage[index]} GB")
                    case "Disk":
                        disk_usage = dataFrame["Site_Disk_Usage"]
                        for index, row in dataFrame.iterrows():
                            self.writeline(f"{row['Site Name']}\t\t{disk_usage[index]:.0f} TB")
                    case "VM":
                        vm_count = dataFrame["Site_VM_Count"]
                        for index, row in dataFrame.iterrows():
                            self.writeline(f"{row['Site Name']}\t\t{vm_count[index]} VMs")
                    case _:
                        self.writeline("No data available for the specified resource.")
            else:
                self.writeline("No data available for the specified resource.")
            self.writeline("")
