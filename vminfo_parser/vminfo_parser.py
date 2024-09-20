#!/usr/bin/env python3
# Std lib imports
import io
import logging
import re
import sys
import typing as t
import weakref

# 3rd party imports
import magic
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from . import const
from .config import Config

A = t.TypeVar("Analyzer", bound="Analyzer")
LOGGER = logging.getLogger(__name__)


class VMData:
    def __init__(self: t.Self, df: pd.DataFrame) -> None:
        self.df: pd.DataFrame = df
        self.column_headers: dict[str, str] = {}

    @classmethod
    def get_file_type(cls: t.Self, file_path: str) -> str:
        """
        Returns the MIME type of the file located at the specified file path.

        Args:
            file_path (str): The path to the file for which the MIME type should be determined.

        Returns:
            str: The MIME type of the file.

        Raises:
            FileNotFoundError: If the file at the specified file path does not exist.
        """
        mime_type = magic.from_file(file_path, mime=True)
        return mime_type

    @classmethod
    def from_file(cls: t.Self, file_path: str) -> "VMData":
        file_type = cls.get_file_type(file_path)
        if file_type == const.MIME.get("csv"):
            df = pd.read_csv(file_path)
        elif file_type in const.MIME.get("excel"):
            df = pd.read_excel(file_path)
        else:
            LOGGER.critical("File passed in was neither a CSV nor an Excel file")
            exit()
        return cls(df)

    def set_column_headings(self: t.Self) -> None:
        for version, headers in const.COLUMN_HEADERS.items():
            if all(col in self.df.columns for col in headers.values()):
                self.column_headers = headers.copy()
                self.column_headers["unitType"] = "GB" if version == "VERSION_1" else "MB"
                break
        else:
            LOGGER.error(
                "Missing column headers from either %s",
                " or ".join(
                    [str([header for header in version.values()]) for version in const.COLUMN_HEADERS.values()]
                ),
            )
            raise ValueError("Headers don't match either of the versions expected")

    def add_extra_columns(self: t.Self) -> None:
        os_column = self.column_headers["operatingSystem"]

        if not all(col in self.df.columns for col in const.EXTRA_COLUMNS_DEST):
            self.df[const.EXTRA_COLUMNS_DEST] = self.df[os_column].str.extract(const.EXTRA_COLUMNS_NON_WINDOWS_REGEX)
            self.df[const.EXTRA_WINDOWS_SERVER_COLUMNS] = self.df[os_column].str.extract(
                const.EXTRA_COLUMNS_WINDOWS_SERVER_REGEX
            )
            self.df[const.EXTRA_WINDOWS_DESKTOP_COLUMNS] = self.df[os_column].str.extract(
                const.EXTRA_COLUMNS_WINDOWS_DESKTOP_REGEX, flags=re.IGNORECASE
            )

            for idx, column in enumerate(const.EXTRA_COLUMNS_DEST):
                self.df[column] = self.df[const.EXTRA_WINDOWS_SERVER_COLUMNS[idx]].where(
                    self.df[column].isnull(), self.df[column]
                )
                self.df[column] = self.df[const.EXTRA_WINDOWS_DESKTOP_COLUMNS[idx]].where(
                    self.df[column].isnull(), self.df[column]
                )

            self.df.drop(
                const.EXTRA_WINDOWS_SERVER_COLUMNS + const.EXTRA_WINDOWS_DESKTOP_COLUMNS,
                axis=1,
                inplace=True,
            )
        else:
            LOGGER.info("All columns already exist")

    def create_site_specific_dataframe(self: t.Self) -> pd.DataFrame:
        """
        Adds site-specific columns to the DataFrame by aggregating resource usage metrics.
        This function groups the data by site name and calculates the total memory, disk, and CPU usage for each site.

        Args:
            None: This method does not take any arguments.

        Returns:
            pd.DataFrame: A DataFrame containing the aggregated resource usage for each site, with renamed columns for clarity.

        Examples:
            site_usage_df = create_site_specific_dataframe()
        """
        site_columns = ["Site_RAM_Usage", "Site_Disk_Usage", "Site_CPU_Usage", "Site_VM_Count"]
        new_site_df = self.df.copy()
        # Check if all site-specific columns already exist
        if all(col in new_site_df.columns for col in site_columns):
            self.output.writeline("Site-specific columns already exist in the DataFrame.")
            return

        # Get the column names from the column_headers dictionary
        memory_col = self.column_headers["vmMemory"]
        disk_col = self.column_headers["vmDisk"]
        cpu_col = self.column_headers["vCPU"]
        unit_type = self.column_headers["unitType"]

        if unit_type == "MB":
            # If the disk and ram are in MB, convert the memory to GiB
            # convert the disk to TiB
            new_site_df[memory_col] = np.ceil(new_site_df[memory_col] / 1024).astype(int)
            new_site_df[disk_col] = np.ceil(new_site_df[disk_col] / 1024 / 1024).astype(int)
        elif unit_type == "GB":
            # If the unit type is GB, we don't need to convert the ram
            # convert the disk to TiB
            new_site_df[disk_col] = np.ceil(new_site_df[disk_col] / 1024).astype(int)
        elif unit_type != "GB":
            raise ValueError(f"Unexpected unit type: {unit_type}")

        # Group by Site Name and calculate sums
        site_usage = new_site_df.groupby("Site Name")[[memory_col, disk_col, cpu_col]].sum().reset_index()
        site_usage["Site_VM_Count"] = new_site_df.groupby("Site Name")["Site Name"].count().values

        # Rename columns to match the desired output
        site_usage.columns = ["Site Name"] + site_columns

        return site_usage

    def save_to_csv(self: t.Self, path: str) -> None:
        self.df.to_csv(path, index=False)


class CLIOutput:
    def __init__(self: t.Self) -> None:
        # Output buffer to store output.
        self.output = io.StringIO(initial_value="\n\n", newline="\n")

        # Finalizer for flushing buffer to stdout.
        # Will be called when self is deleted or when the interpreter exits
        self._finalize = weakref.finalize(self, self.flush_output, self.output)

    @staticmethod
    def flush_output(output: io.StringIO, file: t.Optional[io.TextIOBase] = None) -> None:
        """Write StringIO Buffer to file (or stdout).  Closes output buffer.

        Args:
            output (io.StringIO): StringIO obj containing output buffer
            file (t.Optional[io.TextIOBase], optional): File to write butter to. Defaults to stdout.
        """
        # Delay setting referece to stdout so tests can capture it
        if file is None:
            file = sys.stdout
        file.write(output.getvalue())
        output.close()

    def writeline(self: t.Self, line: str = "") -> None:
        """write string to output buffer.  Adds newline if line does not end with one.

        Args:
            line (str, optional): string to write to output buffer. Defaults to "".
        """
        if not line.endswith("\n"):
            line = line + "\n"
        self.write(line)

    def write(self: t.Self, line: str) -> None:
        """Write string to output buffer.

        Args:
            line (str): string to write to output buffer
        """
        self.output.write(line)

    def close(self: t.Self) -> None:
        """Calls private finalizer for output buffer.  Finalizer will be closed and cannot be called again."""
        self._finalize()

    def format_dataframe_output(self: t.Self, dataFrame: pd.DataFrame, os_name: t.Optional[str] = None) -> None:
        if dataFrame.index.nlevels == 2:
            pass
        else:
            os_version = dataFrame["OS Version"].values
            count = dataFrame["Count"].values

            self.writeline("")
            self.writeline(os_name)
            self.writeline("--------------")
            self.writeline("OS Version\t\t\t Count")

            for version, count_value in zip(os_version, count):
                self.writeline(f"{version.ljust(32)} {count_value}")

    def generate_os_version_distribution(self: t.Self, analyzer: A, os_name: str) -> pd.DataFrame:
        filtered_df = analyzer.vm_data.df[(analyzer.vm_data.df["OS Name"] == os_name)]
        counts = filtered_df["OS Version"].fillna("unknown").value_counts().reset_index()
        counts.columns = ["OS Version", "Count"]

        if analyzer.config.minimum_count is not None and analyzer.config.minimum_count > 0:
            counts = counts[counts["Count"] >= analyzer.config.minimum_count]

        return counts

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



class Visualizer:
    def __init__(self: t.Self, analyzer: A) -> None:
        self.analyzer = analyzer
        self.cli_output = CLIOutput()

    def visualize_disk_space(
        self: t.Self,
        disk_space_ranges: t.Optional[list[tuple[int, int]]] = None,
    ) -> None:
        if disk_space_ranges is None:
            disk_space_ranges = self.analyzer.calculate_disk_space_ranges()

        # Count the number of VMs in each disk space range
        range_counts = {range_: 0 for range_ in disk_space_ranges}
        for lower, upper in disk_space_ranges:
            mask = (self.analyzer.vm_data.df[self.analyzer.vm_data.column_headers["vmDisk"]] >= lower) & (
                self.analyzer.vm_data.df[self.analyzer.vm_data.column_headers["vmDisk"]] <= upper
            )
            count = self.analyzer.vm_data.df.loc[mask].shape[0]
            range_counts[(lower, upper)] = count

        # Sort the counts and plot them as a horizontal bar chart
        sorted_dict = dict(sorted(range_counts.items(), key=lambda x: x[1]))

        if self.analyzer.vm_data.df.empty:
            LOGGER.warning("No data to plot")
            return

        # Create a subplot for plotting
        fig, ax = plt.subplots()

        # Plot the sorted counts as a horizontal bar chart
        for range_, count in sorted_dict.items():
            ax.barh(f"{range_[0]}-{range_[1]} GB", count)

        # Set titles and labels for the plot
        ax.set_ylabel("Disk Space Range")
        ax.set_xlabel("Number of VMs")
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

        ax.set_title("Hard Drive Space Breakdown for Organization")

        ax.set_xlim(right=max(range_counts.values()) + 1.5)

        # Display the plot
        plt.show(block=True)
        plt.close()

    def visualize_disk_space_distribution(
        self: t.Self,
        range_counts_by_environment: pd.DataFrame,
        environment_filter: str,
        os_filter: t.Optional[str] = None,
    ) -> None:
        if self.analyzer.config.generate_graphs:
            range_counts_by_environment.plot(kind="bar", stacked=False, figsize=(12, 8), rot=45)

            plt.xlabel("Disk Space Range")
            plt.ylabel("Number of VMs")
            plt.title(f'VM Disk Size Ranges Sorted by Environment {f"for {os_filter}" if os_filter else ""}')

            plt.show(block=True)
            plt.close()

    def visualize_os_distribution(
        self: t.Self,
        counts: pd.Series,
        os_names: list[str],
        environment_filter: t.Optional[str] = None,
        min_count: int = 500,
    ) -> None:
        # Define specific colors for identified OS names
        # Generate random colors for bars not in SUPPORTED_OS_COLORS
        random_colors = cm.rainbow(np.linspace(0, 1, len(counts)))
        colors = [const.SUPPORTED_OS_COLORS.get(os, random_colors[i]) for i, os in enumerate(os_names)]

        # Plot the counts as a horizontal bar chart with specified and random colors
        # ax = counts.plot(kind="barh", rot=45, color=colors)
        counts.plot(kind="barh", rot=45, color=colors)

        if self.analyzer.vm_data.df.empty:
            LOGGER.warning("No data to plot")
            return

        # Set titles and labels for the plot
        plt.title(f"OS Counts by Environment Type (>= {min_count})")
        plt.xlabel("Count")
        plt.ylabel("Operating Systems")

        # Display the plot
        plt.show(block=True)
        plt.close()

    def visualize_os_distribution_log_scale(
        self: t.Self,
        counts: pd.Series,
        os_names: list[str],
        environment_filter: t.Optional[str] = None,
        min_count: int = 500,
    ) -> None:
        random_colors = cm.rainbow(np.linspace(0, 1, len(counts)))
        colors = [const.SUPPORTED_OS_COLORS.get(os, random_colors[i]) for i, os in enumerate(os_names)]

        # ax = counts.plot(kind="barh", rot=45, color=colors)
        counts.plot(kind="barh", rot=45, color=colors)

        plt.title(f"OS Counts by Environment Type (>= {min_count})")
        plt.xlabel("Count")
        plt.ylabel("Operating Systems")

        plt.xscale("log")
        plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())

        if self.analyzer.config.generate_graphs:
            plt.show(block=True)
            plt.close()

    def visualize_unsupported_os_distribution(self: t.Self, unsupported_counts: pd.Series) -> None:
        if self.analyzer.config.generate_graphs:
            random_colors = cm.rainbow(np.linspace(0, 1, len(unsupported_counts)))
            plt.pie(
                unsupported_counts,
                labels=unsupported_counts.index,
                colors=random_colors,
                autopct="%1.1f%%",
            )
            plt.title("Unsupported Operating System Distribution")

            plt.show(block=True)
            plt.close()

    def visualize_supported_os_distribution(
        self: t.Self,
        counts: pd.Series,
        environment_filter: t.Optional[str] = None,
    ) -> None:
        if self.analyzer.config.generate_graphs:
            colors = [const.SUPPORTED_OS_COLORS[os] for os in counts.index]

            if environment_filter and environment_filter != "both":
                counts.plot(kind="barh", rot=45, color=colors)
            else:
                counts.plot(kind="barh", rot=45)

            if environment_filter not in ["prod", "non-prod"]:
                plt.title("Supported Operating Systems For All Environments")
            else:
                plt.title(f"Supported Operating Systems for {environment_filter.title()}")

            plt.ylabel("Operating Systems")
            plt.xlabel("Count")
            plt.xscale("log")
            plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())

            if environment_filter != "both":
                plt.xticks(
                    [
                        counts.iloc[0] - (counts.iloc[0] % 100),
                        counts.iloc[len(counts) // 2] - (counts.iloc[len(counts) // 2] % 100),
                        counts.iloc[-1],
                    ]
                )

            plt.show(block=True)
            plt.close()

    def visualize_os_version_distribution(self: t.Self, os_name: str) -> None:
        counts = self.cli_output.generate_os_version_distribution(self.analyzer, os_name)

        if not counts.empty:
            ax = counts.plot(kind="barh", rot=45)

            if self.analyzer.config.generate_graphs:
                plt.title(f"Distribution of {os_name}")
                plt.ylabel("OS Version")
                plt.xlabel("Count")

                plt.xticks(rotation=0)
                ax.set_yticklabels(counts["OS Version"])

                plt.show(block=True)
                plt.close()

        self.cli_output.format_dataframe_output(counts, os_name=os_name)


class Analyzer:
    def __init__(
        self: t.Self,
        vm_data: VMData,
        config: Config,
        column_headers: t.Optional[dict[str, str]] = None,
    ) -> None:
        self.vm_data = vm_data
        self.config = config
        self.column_headers = column_headers
        self.visualizer = Visualizer(self)
        self.cli_output = CLIOutput()

    def calculate_average_ram(self: t.Self, environment_type: str) -> None:
        os_values = self.vm_data.df["OS Name"].unique()

        self.cli_output.writeline("{:<20} {:<10}".format("OS", "Average RAM (GB)"))
        self.cli_output.writeline("-" * 30)

        for os in os_values:
            filtered_hosts = self.vm_data.df[
                (self.vm_data.df["OS Name"] == os)
                & (self.vm_data.df[self.column_headers["environment"]].str.contains(environment_type))
            ]

            if not filtered_hosts.empty:
                avg_ram = filtered_hosts[self.column_headers["vmMemory"]].mean()
                self.cli_output.writeline("{:<20} {:<10.2f}".format(os, avg_ram))

    def calculate_disk_space_ranges(
        self: t.Self,
        dataFrame: t.Optional[pd.DataFrame] = None,
        show_disk_in_tb: bool = False,
        over_under_tb: bool = False,
    ) -> list[tuple[int, int]]:
        if dataFrame is None:
            # default to the dataframe in the attribute unless overridden
            dataFrame = self.vm_data.df
        frameHeading = self.column_headers["vmDisk"]

        # sometimes the values in this column are interpreted as a string and have a comma inserted
        # we want to check and replace the comma
        for index, row in dataFrame.iterrows():
            if isinstance(row[frameHeading], str):
                dataFrame.at[index, frameHeading] = row[frameHeading].replace(",", "")

        dataFrame[frameHeading] = pd.to_numeric(dataFrame[frameHeading], errors="coerce")
        unit = self.column_headers["unitType"]

        min_disk_space = round(int(dataFrame[frameHeading].min()))
        max_disk_space = round(int(dataFrame[frameHeading].max()))

        final_range = (9001, max_disk_space) if max_disk_space > 9000 else (10001, 15000)

        if show_disk_in_tb:
            disk_space_ranges = [
                (min_disk_space, 2000),
                (2001, 9000),
                final_range,
            ]
        elif over_under_tb:
            disk_space_ranges = [(min_disk_space, 1000), (1001, max_disk_space)]
        else:
            disk_space_ranges = [
                (min_disk_space, 200),
                (201, 400),
                (401, 600),
                (601, 900),
                (901, 1500),
                (1501, 2000),
                (2001, 3000),
                (3001, 5000),
                (5001, 9000),
                final_range,
            ]

        disk_space_ranges_with_vms = []
        for range_start, range_end in disk_space_ranges:
            epsilon = 1
            if unit == "MB":
                vms_in_range = dataFrame[
                    (dataFrame[frameHeading] / 1024 >= range_start - epsilon)
                    & (dataFrame[frameHeading] / 1024 <= range_end + epsilon)
                ]
            else:
                vms_in_range = dataFrame[
                    (dataFrame[frameHeading] >= range_start - epsilon)
                    & (dataFrame[frameHeading] <= range_end + epsilon)
                ]

            if not vms_in_range.empty:
                disk_space_ranges_with_vms.append((range_start, range_end))

        return disk_space_ranges_with_vms

    def categorize_environment(self: t.Self, x: str, *args: str) -> str:
        if pd.isnull(x):
            return "non-prod"

        if not args:
            return "all envs"

        # Ensure x is a string
        if isinstance(x, str):
            for arg in args:
                if arg in x:
                    return "prod"

        return "non-prod"

    def handle_disk_space(
        self: t.Self,
        dataFrame: pd.DataFrame,
        environment_filter: str,
        env_keywords: list[str],
        os_filter: t.Optional[str] = None,
        show_disk_in_tb: bool = False,
        over_under_tb: bool = False,
    ) -> None:
        # NOTE: I am taking in the dataFrame as it is a mutated copy of the original dataFrame stored in self.vmdata.df
        # This copy has a paired down version of the information and then environments have been changed to prod/non-prod
        diskHeading = self.column_headers["vmDisk"]
        envHeading = self.column_headers["environment"]
        unit = self.column_headers["unitType"]

        disk_space_ranges = self.calculate_disk_space_ranges(
            dataFrame=dataFrame,
            show_disk_in_tb=show_disk_in_tb,
            over_under_tb=over_under_tb,
        )

        for lower, upper in disk_space_ranges:
            if unit == "MB":
                mask = (round(dataFrame[diskHeading] / 1024) >= lower) & (round(dataFrame[diskHeading] / 1024) <= upper)
            else:
                mask = (dataFrame[diskHeading] >= lower) & (dataFrame[diskHeading] <= upper)

            dataFrame.loc[mask, "Disk Space Range"] = f"{lower}-{upper} GB"

        if environment_filter is None:
            environment_filter = "all"

        if environment_filter == "both":
            range_counts_by_environment = (
                dataFrame.groupby(["Disk Space Range", envHeading]).size().unstack(fill_value=0)
            )
        elif environment_filter == "all":
            range_counts_by_environment = dataFrame["Disk Space Range"].value_counts().reset_index()
            range_counts_by_environment.columns = ["Disk Space Range", "Count"]
            range_counts_by_environment.set_index("Disk Space Range", inplace=True)
        else:
            range_counts_by_environment = (
                dataFrame[dataFrame[envHeading] == environment_filter]
                .groupby(["Disk Space Range", envHeading])
                .size()
                .unstack(fill_value=0)
            )

        range_counts_by_environment["second_number"] = (
            range_counts_by_environment.index.str.split("-").str[1].str.split().str[0].astype(int)
        )
        sorted_range_counts_by_environment = range_counts_by_environment.sort_values(by="second_number", ascending=True)
        sorted_range_counts_by_environment.drop("second_number", axis=1, inplace=True)

        if os_filter:
            self.cli_output.print_formatted_disk_space(
                sorted_range_counts_by_environment,
                environment_filter,
                env_keywords,
                os_filter=os_filter,
            )
        else:
            self.cli_output.print_formatted_disk_space(
                sorted_range_counts_by_environment,
                environment_filter,
                env_keywords,
            )

        # Call the new visualize method
        if environment_filter == "all":
            self.visualizer.visualize_disk_space()
        else:
            self.visualizer.visualize_disk_space_distribution(
                sorted_range_counts_by_environment,
                environment_filter,
                os_filter=os_filter,
            )

    def handle_operating_system_counts(self: t.Self, environment_filter: str, dataFrame: pd.DataFrame = None) -> None:
        counts, os_names = self._calculate_os_counts(environment_filter, dataFrame)

        clean_output = "\n".join(
            [
                line.strip()
                for line in str(counts).split("\n")
                if not line.startswith("Name:") and not line.startswith("dtype")
            ]
        )
        self.cli_output.writeline(clean_output)

        min_count = self.config.minimum_count if self.config.minimum_count else 500

        if self.config.generate_graphs:
            self.visualizer.visualize_os_distribution(counts, os_names, environment_filter, min_count)

    def _calculate_os_counts(
        self: t.Self, environment_filter: str, dataFrame: pd.DataFrame = None
    ) -> tuple[pd.Series, list[str]]:
        if dataFrame is None:
            dataFrame = self.vm_data.df

        min_count = self.config.minimum_count if self.config.minimum_count else 500

        if not environment_filter or environment_filter == "all":
            counts = dataFrame["OS Name"].value_counts()
            counts = counts[counts >= min_count]
        else:
            counts = dataFrame.groupby(["OS Name", self.column_headers["environment"]]).size().unstack().fillna(0)
            counts["total"] = counts.sum(axis=1)
            counts["combined_total"] = counts["prod"] + counts["non-prod"]
            counts = counts[(counts["total"] >= min_count) & (counts["combined_total"] >= min_count)].drop(
                ["total", "combined_total"], axis=1
            )
            counts = counts.sort_values(by="prod", ascending=False)

        os_names = [idx[1] for idx in counts.index] if counts.index.nlevels == 2 else counts.index

        return counts, os_names

    def generate_supported_OS_counts(
        self: t.Self,
        *env_keywords: str,
        environment_filter: t.Optional[str] = None,
    ) -> pd.Series:
        data_cp = self.vm_data.df.copy()
        if environment_filter and env_keywords:
            data_cp[self.column_headers["environment"]] = self.vm_data.df[self.column_headers["environment"]].apply(
                self.categorize_environment, args=env_keywords
            )

        if environment_filter and environment_filter not in ["all", "both"]:
            data_cp = data_cp[data_cp[self.column_headers["environment"]] == environment_filter]
        elif environment_filter == "both":
            data_cp = data_cp.groupby(["OS Name", self.column_headers["environment"]]).size().unstack().fillna(0)

        if data_cp.empty:
            LOGGER.warning("None found in %s", environment_filter)
            return pd.Series()

        if environment_filter and environment_filter != "both":
            filtered_counts = data_cp["OS Name"].value_counts()
        else:
            filtered_counts = data_cp

        filtered_counts = filtered_counts[filtered_counts.index.isin(const.SUPPORTED_OSES)]
        filtered_counts = filtered_counts.astype(int)

        # This removes unwanted lines from the output that Pandas generates
        clean_output = "\n".join(
            [
                line.strip()
                for line in str(filtered_counts).split("\n")
                if not line.startswith("Name:") and not line.startswith("dtype")
            ]
        )
        self.cli_output.writeline(clean_output)

        return filtered_counts

    def generate_unsupported_OS_counts(self: t.Self) -> pd.Series:
        counts = self.vm_data.df["OS Name"].value_counts()

        unsupported_counts = counts[~counts.index.isin(const.SUPPORTED_OSES)]

        other_counts = unsupported_counts[unsupported_counts <= 500]
        other_total = other_counts.sum()
        unsupported_counts = unsupported_counts[unsupported_counts > 500]
        unsupported_counts["Other"] = other_total

        clean_output = "\n".join(
            [
                line.strip()
                for line in str(unsupported_counts).split("\n")
                if not line.startswith("Name:") and not line.startswith("dtype")
            ]
        )

        self.cli_output.writeline(clean_output)

        return unsupported_counts

    def sort_attribute_by_environment(
        self: t.Self,
        *env_keywords: str,
        attribute: str = "operatingSystem",
        os_filter: t.Optional[str] = None,
        environment_filter: t.Optional[str] = None,
        show_disk_in_tb: bool = False,
        over_under_tb: bool = False,
        frameHeading: str = "VM Provisioned (GB)",
    ) -> None:
        env_column = "Environment"
        data_cp = self.vm_data.df.copy()

        if env_column not in self.vm_data.df.columns:
            if "ent-env" in self.vm_data.df.columns:
                env_column = "ent-env"
            else:
                raise ValueError("Neither 'Environment' nor 'ent-env' found in DataFrame columns.")

        data_cp[env_column] = self.vm_data.df[env_column].apply(self.categorize_environment, args=env_keywords)

        if os_filter:
            data_cp = data_cp[data_cp["OS Name"] == os_filter]

        if environment_filter and environment_filter not in ["all", "both"]:
            data_cp = data_cp[data_cp[env_column] == environment_filter]

        if data_cp.empty:
            LOGGER.warning("None found in %s", environment_filter)
            return

        if attribute == "diskSpace":
            self.handle_disk_space(
                data_cp,
                environment_filter,
                env_keywords,
                os_filter,
                show_disk_in_tb=show_disk_in_tb,
                over_under_tb=over_under_tb,
            )
        if attribute == "operatingSystem":
            self.handle_operating_system_counts(environment_filter, dataFrame=data_cp)


def main(*args: t.Optional[str]) -> None:  # noqa: C901
    config = Config()
    config = Config.from_args(*args)

    vm_data = VMData.from_file(config.file)
    vm_data.set_column_headings()
    vm_data.add_extra_columns()

    analyzer = Analyzer(vm_data, config, column_headers=vm_data.column_headers)
    visualizer = Visualizer(analyzer)

    # Load environments from prod-env-labels if provided
    environments = []
    if config.prod_env_labels:
        environments = config.prod_env_labels.split(",")

    if config.sort_by_site:
        site_dataframe = vm_data.create_site_specific_dataframe()
        analyzer.cli_output.print_site_usage(["Memory", "CPU", "Disk", "VM"], site_dataframe)
        # analyzer.cli_output.print_site_usage("Memory", site_dataframe)
        # analyzer.cli_output.print_site_usage("CPU", site_dataframe)
        # analyzer.cli_output.print_site_usage("Disk", site_dataframe)
        # analyzer.cli_output.print_site_usage("VM", site_dataframe)

    # Check if environments are defined for sorting
    if config.sort_by_env and not environments:
        LOGGER.critical(
            "You specified you wanted to sort by environment but "
            "did not provide a definition of what categorizes a Prod environment... exiting"
        )
        exit()

    if config.show_disk_space_by_os:
        if config.os_name:
            # If the user specifies an OS, use that to filter out everything else
            if environments:
                if config.sort_by_env:
                    analyzer.plot_disk_space_distribution(
                        os_name=config.os_name,
                        environment_filter=config.sort_by_env,
                        show_disk_in_tb=config.breakdown_by_terabyte,
                    )
                else:
                    analyzer.plot_disk_space_distribution(
                        os_name=config.os_name,
                        show_disk_in_tb=config.breakdown_by_terabyte,
                    )
            else:
                analyzer.plot_disk_space_distribution(
                    os_name=config.os_name,
                    show_disk_in_tb=config.breakdown_by_terabyte,
                )
        else:
            # If the user has not specified an OS name, assume they want them all
            for os_name in vm_data.df["OS Name"].unique():
                if environments:
                    # analyzer.plot_disk_space_distribution(os_name=os_name, show_disk_in_tb=config.breakdown_by_terabyte)
                    analyzer.sort_attribute_by_environment(
                        attribute="diskSpace",
                        os_filter=os_name,
                        environment_filter=config.sort_by_env,
                        over_under_tb=config.over_under_tb,
                        *environments,  # noqa: B026
                    )

                else:
                    if config.over_under_tb:
                        analyzer.sort_attribute_by_environment(
                            os_name=os_name,
                            show_disk_in_tb=config.breakdown_by_terabyte,
                        )
                    else:
                        analyzer.sort_attribute_by_environment(os_name=os_name)

    if config.get_disk_space_ranges:
        if config.sort_by_env != "all":
            if environments:
                analyzer.sort_attribute_by_environment(
                    attribute="diskSpace",
                    environment_filter=config.sort_by_env,
                    over_under_tb=config.over_under_tb,
                    show_disk_in_tb=config.breakdown_by_terabyte,
                    *environments,  # noqa: B026
                )
            else:
                LOGGER.critical(
                    "Failed to determine prod from non-prod environments... Perhaps you did not pass in the --prod-env-labels ?"
                )
                exit()
        else:
            analyzer.sort_attribute_by_environment(
                attribute="diskSpace",
                environment_filter=config.sort_by_env,
                over_under_tb=config.over_under_tb,
                show_disk_in_tb=config.breakdown_by_terabyte,
            )

    if config.get_os_counts:
        if environments:
            if config.os_name:
                analyzer.sort_attribute_by_environment(
                    attribute="operatingSystem",
                    os_filter=config.os_name,
                    *environments,  # noqa: B026
                )
                # visualizer.visualize_os_distribution()
            elif config.sort_by_env:
                analyzer.sort_attribute_by_environment(
                    attribute="operatingSystem",
                    *environments,  # noqa: B026
                    environment_filter=config.sort_by_env,
                )
                # visualizer.visualize_os_distribution()
            else:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem", *environments)  # noqa: B026
                # visualizer.visualize_os_distribution()
        else:
            if config.os_name:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem", os_filter=config.os_name)
                # visualizer.visualize_os_distribution()
            else:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem")
                ###
                # visualizer.visualize_os_distribution()

    if config.output_os_by_version:
        for os_name in vm_data.df["OS Name"].unique():
            visualizer.visualize_os_version_distribution(os_name)

    if config.get_supported_os:
        if config.prod_env_labels and config.sort_by_env:
            supported_counts = analyzer.generate_supported_OS_counts(
                *config.prod_env_labels.split(","),
                environment_filter=config.sort_by_env,
            )
            visualizer.visualize_supported_os_distribution(supported_counts, environment_filter=config.sort_by_env)
        else:
            supported_counts = analyzer.generate_supported_OS_counts(environment_filter=config.sort_by_env)
            visualizer.visualize_supported_os_distribution(supported_counts, environment_filter=config.sort_by_env)

    if config.get_unsupported_os:
        unsupported_counts = analyzer.generate_unsupported_OS_counts()
        visualizer.visualize_unsupported_os_distribution(unsupported_counts)

    # Save results if necessary
    vm_data.save_to_csv("output.csv")

    # close clioutput
    analyzer.cli_output.close()
    visualizer.cli_output.close()


if __name__ == "__main__":
    main()
