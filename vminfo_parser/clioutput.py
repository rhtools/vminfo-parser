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

    def format_series_output(self: t.Self, counts: pd.Series) -> None:
        for line in str(counts).split("\n"):
            if not line.startswith("Name:") and not line.startswith("dtype"):
                self.writeline(line.strip())

    def format_rows(
        self: t.Self,
        dataFrame: pd.DataFrame,
        formatted_rows: list,
        justification: int,
        col_widths: dict,
    ):
        """
        Format the rows of a DataFrame into a string representation with specified widths.

        This function iterates over each row in the provided DataFrame, formats the row values according to
        the specified column widths, and appends the formatted rows to the provided list. The resulting string
        representation of the formatted rows is returned.

        Args:
            dataFrame (pd.DataFrame): The DataFrame containing the data to format.
            formatted_rows (list): A list to which the formatted row strings will be appended.
            justification (int): The width for left-justifying the index values.
            col_widths (dict): A dictionary mapping column names to their respective widths.

        Returns:
            str: A string representation of the formatted rows, joined by newline characters.
        """
        for index, row in dataFrame.iterrows():
            formatted_row = [str(index).ljust(justification)]
            for col_name, width in col_widths.items():
                value = str(row[col_name]) if col_name in row.index else ""
                formatted_row.append(value.ljust(width))
            formatted_rows.append(" ".join(formatted_row))

        formatted_df_str = "\n".join(formatted_rows)

        return formatted_df_str

    def set_column_width(
        self: t.Self,
        dataFame: pd.DataFrame,
        index_column_padding: int,
        remaining_column_padding: int,
        index_column_name: str = None,
    ) -> dict:
        """
        Set the widths for the columns in a DataFrame based on specified parameters.
        This function returns a dictionary mapping column names to their respective widths for formatting purposes.

        Args:
            dataFame (pd.DataFrame): The DataFrame for which column widths are to be set.
            index_column_width (int): The width to be assigned to the index column.
            remaining_column_widths (int): The width to be assigned to the remaining columns.
            index_column_name (str, optional): The name of the index column. If provided, it will be assigned the
                specified width. Defaults to None.

        Returns:
            dict: A dictionary mapping each column name to its corresponding width.

        Examples:
            >>> set_column_width(dataFame=my_dataframe, index_column_width=20, remaining_column_widths=10,
                index_column_name="Environment")
            {'Environment': 20, 'Column1': max(10, len('Column1')), 'Column2': max(10, len('Column2'))}
        """
        if index_column_name:
            col_widths = {
                index_column_name: index_column_padding,
                **{env: max(remaining_column_padding, len(env)) for env in dataFame.columns},
            }
        else:
            col_widths = {env: max(index_column_padding, len(env)) for env in dataFame.columns}

        return col_widths

    def print_formatted_disk_space(
        self: t.Self,
        col_widths: dict,
        formatted_df_str: str,
        os_filter: t.Optional[str] = None,
        display_header: bool = True,
        index_heading_justification: int = 39,
        other_headings_justification: int = 11,
    ) -> None:
        """
        Print the formatted disk space information to the output.
        This function displays a header and the formatted data, optionally filtered by the operating system.

        Args:
            col_widths (dict): A dictionary containing the widths for each column in the output.
            formatted_df_str (str): A string representation of the formatted disk space data.
            os_filter (Optional[str]): An optional filter to display specific operating system information.

        Returns:
            None
        """
        temp_heading = ""
        if os_filter:
            self.writeline(os_filter)
            self.writeline("---------------------------------")
        if display_header:
            for headings in list(col_widths.keys()):
                if temp_heading:
                    temp_heading += headings.ljust(other_headings_justification)
                else:
                    temp_heading += headings.ljust(index_heading_justification)
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
            dataFrame (pd.DataFrame): A DataFrame containing the relevant data for the site, including
                                      resource usage metrics.

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
