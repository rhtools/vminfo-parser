# Std lib imports
import logging
import typing as t
from collections.abc import Callable

# 3rd party imports
import pandas as pd

from . import const
from .clioutput import CLIOutput
from .config import Config
from .visualizer import Visualizer
from .vmdata import VMData

LOGGER = logging.getLogger(__name__)


class Analyzer:
    def __init__(
        self: t.Self,
        vm_data: VMData,
        config: Config,
    ) -> None:
        self.vm_data = vm_data
        self.config = config
        self.visualizer = Visualizer()
        self.cli_output = CLIOutput()

    def calculate_average_ram(self: t.Self, environment_type: str) -> None:
        os_values = self.vm_data.df["OS Name"].unique()

        self.cli_output.writeline("{:<20} {:<10}".format("OS", "Average RAM (GB)"))
        self.cli_output.writeline("-" * 30)

        for os in os_values:
            filtered_hosts = self.vm_data.df[
                (self.vm_data.df["OS Name"] == os)
                & (self.vm_data.df[self.vm_data.column_headers["environment"]].str.contains(environment_type))
            ]

            if not filtered_hosts.empty:
                avg_ram = filtered_hosts[self.vm_data.column_headers["vmMemory"]].mean()
                self.cli_output.writeline("{:<20} {:<10.2f}".format(os, avg_ram))

    def generate_dynamic_ranges(
        self: t.Self, max_disk_space: int, show_disk_in_tb: bool = False, over_under_tb: bool = False
    ) -> list[tuple[int, int]]:
        """
        Generate dynamic disk space ranges based on the maximum disk space and specified display options.
        This function returns a list of tuples representing the ranges of disk space in either terabytes or gigabytes.

        Args:
            max_disk_space (int): The maximum disk space to consider for generating ranges.
            show_disk_in_tb (bool, optional): If True, the ranges will be in terabytes. Defaults to False.
            over_under_tb (bool, optional): If True, generates a simplified range for over/under thresholds.
                Defaults to False.

        Returns:
            list: A list of tuples representing the dynamic disk space ranges.

        Examples:
            >>> generate_dynamic_ranges(150000, show_disk_in_tb=True)
            [(0, 2000), (2001, 10000), (10001, 20000), (20001, 50000), (50001, 150000)]
        """
        disk_space_ranges_dict = {
            "tb": [
                (0, 2000),
                (2001, 10000),
                (10001, 20000),
                (20001, 50000),
                (50001, 100000),
                (100001, max_disk_space),
            ],
            "gb": [
                (0, 200),
                (201, 400),
                (401, 600),
                (601, 800),
                (801, 1000),
                (1001, 2000),
                (2001, 3000),
                (3001, 5000),
                (5001, 10000),
                (10001, 20000),
                (20001, 50000),
                (50001, 100000),
                (100001, max_disk_space),
            ],
        }
        disk_space_ranges = []
        # In this section we are dynamically removing unneeded ranges
        # from the total list of ranges based on the dataframe
        if show_disk_in_tb:
            ranges = disk_space_ranges_dict["tb"]
            if max_disk_space > 100000:
                disk_space_ranges = ranges
            # If the largest disk is greater than 50000 but less than 100000 remove the last 2
            # entries and then add the new one
            elif max_disk_space > 50000:
                disk_space_ranges = ranges[:-2] + [(50000, max_disk_space)]
            # If we are greater than 20000 but less than 50000 take the first 3 entries
            # and add on our custom one
            elif max_disk_space > 20000:
                disk_space_ranges = ranges[:3] + [(20001, max_disk_space)]
        elif over_under_tb:
            disk_space_ranges = [(0, 1000), (1001, max_disk_space)]
        # The Same logic applies to the 'gb' items as to the 'tb' items
        # however, given that this is more fine-grained, there are more ranges to add
        else:
            ranges = disk_space_ranges_dict["gb"]
            if max_disk_space > 100000:
                disk_space_ranges = ranges
            elif max_disk_space > 50000:
                disk_space_ranges = ranges[:-2] + [(50001, max_disk_space)]
            elif max_disk_space > 20000:
                disk_space_ranges = ranges[:10] + [(20001, max_disk_space)]
            elif max_disk_space > 10000:
                disk_space_ranges = ranges[:9] + [(10001, max_disk_space)]
            else:
                disk_space_ranges = ranges[:8] + [(5001, max_disk_space)]

        return disk_space_ranges

    def calculate_disk_space_ranges(
        self: t.Self,
        dataFrame: pd.DataFrame | None = None,
        show_disk_in_tb: bool = False,
        over_under_tb: bool = False,
    ) -> list[tuple[int, int]]:
        """
        Calculate the ranges of disk space based on the provided DataFrame and specified display options.
        This function processes the DataFrame to determine which disk space ranges contain virtual machines.

        Args:
            dataFrame (pd.DataFrame, optional): The DataFrame containing disk space data.
                If None, the default DataFrame from the instance will be used. Defaults to None.
            show_disk_in_tb (bool, optional): If True, the ranges will be calculated in terabytes. Defaults to False.
            over_under_tb (bool, optional): If True, generates a simplified range for over/under thresholds.
                Defaults to False.

        Returns:
            list[tuple[int, int]]: A list of tuples representing the disk space ranges that contain virtual machines.

        Examples:
            >>> calculate_disk_space_ranges(dataFrame=my_dataframe, show_disk_in_tb=True)
            [(0, 2000), (2001, 10000)]
        """
        if dataFrame is None:
            # default to the dataframe in the attribute unless overridden
            dataFrame = self.vm_data.df
        frameHeading = self.vm_data.column_headers["vmDisk"]
        # sometimes the values in this column are interpreted as a string and have a comma inserted
        # we want to check and replace the comma
        for index, row in dataFrame.iterrows():
            if isinstance(row[frameHeading], str):
                dataFrame.at[index, frameHeading] = row[frameHeading].replace(",", "")

        dataFrame[frameHeading] = pd.to_numeric(dataFrame[frameHeading], errors="coerce")

        # Normalize the Disk Column to GiB before applying further analysis
        if self.vm_data.column_headers["unitType"] == "MB":
            dataFrame[frameHeading] = dataFrame[frameHeading] / 1024
        max_disk_space = round(int(dataFrame[frameHeading].max()))
        disk_space_ranges = self.generate_dynamic_ranges(max_disk_space, show_disk_in_tb, over_under_tb)
        disk_space_ranges_with_vms = []
        for range_start, range_end in disk_space_ranges:
            epsilon = 1

            vms_in_range = dataFrame[
                (dataFrame[frameHeading] >= range_start - epsilon) & (dataFrame[frameHeading] <= range_end + epsilon)
            ]

            if not vms_in_range.empty:
                disk_space_ranges_with_vms.append((range_start, range_end))

        return disk_space_ranges_with_vms

    def convert_to_tb(self: t.Self, value: str) -> str:
        """
        Convert a given storage value in GB to TB if applicable.
        This function processes a string representing a range of storage values and converts them to terabytes
        when the values exceed 999 GB.

        Args:
            value (str): A string representing a storage value, expected in the format "X-Y GB".

        Returns:
            str: The converted storage value in TB or the original value if conversion is not applicable.

        Examples:
            >>> convert_to_tb("500-1500 GB")
            '500 GB - 1 TB'
        """

        parts = value.split(" ")
        if len(parts) == 2 and parts[1] == "GB":
            lower, upper = map(int, parts[0].split("-"))

            if lower > 999:
                lower = round(lower / 1000, 1)
                lower_unit = "TB"
            else:
                lower_unit = "GB"

            if upper > 999:
                upper = round(upper / 1000, 1)
                upper_unit = "TB"
            else:
                upper_unit = "GB"

            # Format the numbers getting rid of decimal point if its 0
            lower = f"{lower:.0f}" if isinstance(lower, int) or lower % 1 == 0 else f"{lower:.1f}"
            upper = f"{upper:.0f}" if isinstance(upper, int) or upper % 1 == 0 else f"{upper:.1f}"

            # If the lower and upper unit are the same, no special unit handling
            if lower_unit == upper_unit:
                return f"{lower} - {upper} {lower_unit}"
            elif lower_unit == "GB" and upper_unit == "TB":
                # If the first digit is a 0, it does not need a unit
                if int(lower) == 0:
                    return f"{lower} - {upper} TB"
                else:
                    return f"{lower} GB - {upper} TB"
            else:
                return f"{lower} {lower_unit} - {upper} {upper_unit}"
        return value

    def sort_by_disk_space_range(self: t.Self, dataFrame: pd.DataFrame) -> pd.DataFrame:
        """
        Sorts the provided DataFrame by disk space range, optionally breaking down by operating system.

        This function groups the data by operating system and version or by environment, counts the occurrences,
        and sorts the results based on the disk space range. It also applies necessary conversions and drops
        specified columns.

        Args:
            dataFrame (pd.DataFrame): The DataFrame containing disk space data to be sorted.

        Returns:
            pd.DataFrame: A sorted dataFrame object based on the disk space range in the dataFrame
        """
        if self.config.disk_space_by_granular_os:

            dataFrame = (
                dataFrame.groupby(["OS Name", "OS Version", "Disk Space Range"]).size().reset_index(name="Count")
            )
            # create an integer of the large end of range for sorting by size of range
            # if the string said '201 - 400 GB' this will grab '400' and use that to sort
            dataFrame["second_number"] = (
                dataFrame["Disk Space Range"].str.split("-").str[1].str.split().str[0].astype(int)
            )
            sorted_range_counts_by_environment = dataFrame.sort_values(
                by=["OS Version", "second_number"], ascending=True
            )
            sorted_range_counts_by_environment["Disk Space Range"] = sorted_range_counts_by_environment[
                "Disk Space Range"
            ].map(self.convert_to_tb)
            sorted_range_counts_by_environment = sorted_range_counts_by_environment.set_index("OS Version")
            sorted_range_counts_by_environment.drop("OS Name", axis=1, inplace=True)

        else:
            envHeading = self.vm_data.column_headers["environment"]

            if self.config.environment_filter == "both":
                range_counts_by_environment = (
                    dataFrame.groupby(["Disk Space Range", envHeading]).size().unstack(fill_value=0)
                )
            elif self.config.environment_filter == "all":
                range_counts_by_environment = dataFrame["Disk Space Range"].value_counts().reset_index()
                range_counts_by_environment.columns = ["Disk Space Range", "Count"]
                range_counts_by_environment.set_index("Disk Space Range", inplace=True)
            else:
                range_counts_by_environment = (
                    dataFrame[dataFrame[envHeading] == self.config.environment_filter]
                    .groupby(["Disk Space Range", envHeading])
                    .size()
                    .unstack(fill_value=0)
                )
            range_counts_by_environment["second_number"] = (
                range_counts_by_environment.index.str.split("-").str[1].str.split().str[0].astype(int)
            )
            sorted_range_counts_by_environment = range_counts_by_environment.sort_values(
                by="second_number", ascending=True
            )

            # Apply the conversion to the index
            sorted_range_counts_by_environment.index = sorted_range_counts_by_environment.index.map(self.convert_to_tb)

        sorted_range_counts_by_environment.drop("second_number", axis=1, inplace=True)

        return sorted_range_counts_by_environment

    def get_disk_space(self: t.Self, os_filter: str) -> pd.DataFrame:
        """
        Processes and formats disk space data from the provided DataFrame based on specified filters.

        This function calculates disk space ranges, groups the data by environment or operating system

        Args:
            None
        Returns:
            pd.DataFrame: A DataFrame containing counts of disk space ranges, optionally sorted by environment
        """
        df = self.vm_data.create_environment_filtered_dataframe(
            self.config.environments, self.config.environment_filter
        )

        if os_filter:
            df = df[df["OS Name"] == os_filter]

        diskHeading = self.vm_data.column_headers["vmDisk"]
        disk_space_ranges = self.calculate_disk_space_ranges(
            dataFrame=df,
            show_disk_in_tb=self.config.breakdown_by_terabyte,
            over_under_tb=self.config.over_under_tb,
        )

        for lower, upper in disk_space_ranges:
            mask = (df[diskHeading] >= lower) & (df[diskHeading] <= upper)
            df.loc[mask, "Disk Space Range"] = f"{lower}-{upper} GB"

        return self.sort_by_disk_space_range(df)

    def get_unique_os_names(self: t.Self) -> list[str]:
        """Generate list of unique os names from dataframe.

        Uses vmdata object if no dataframe is passed.
        Returns single entry if os_name in config object.
        Returns empty list if os_name in config object and os_name not in dataframe.
        Args:
            None

        Returns:
            list[str]: list of unique OS Names
        """

        os_names: list[str] = [
            os_name
            for os_name in self.vm_data.df["OS Name"].unique()
            if os_name is not None and not pd.isna(os_name) and os_name != ""
        ]
        if not os_names:
            return []
        if self.config.os_name:
            if self.config.os_name in os_names:
                return [self.config.os_names]
            return []
        return os_names

    def get_operating_system_counts(self: t.Self) -> pd.Series:
        """Returns the counts of operating systems based on the configured environment filter.

        This function calculates the counts of operating systems and returns the results.

        Args:
            None
        Returns:
            pd.Series: Series object containing counts, indexed by OS
        """
        df = self.vm_data.create_environment_filtered_dataframe(
            self.config.environments, env_filter=self.config.sort_by_env
        )

        if self.config.os_name:
            df = df[df["OS Name"] == self.config.os_name]

        return self._calculate_os_counts(df)

    def _calculate_os_counts(self: t.Self, dataFrame: pd.DataFrame = None) -> pd.Series:
        """Calculates the counts of operating systems based on the provided environment filter.

        This function analyzes the DataFrame to count occurrences of operating systems, applying filters as necessary.
        It returns the counts and the corresponding operating system names, allowing for further processing
        or visualization.

        Args:
            dataFrame (pd.DataFrame, optional): The DataFrame containing the data to analyze. Defaults to None.
        Returns:
            tuple[pd.Series, list[str]]: A tuple containing a Series of counts and a list of operating system names.
        """
        if dataFrame is None:
            dataFrame = self.vm_data.df

        environment_filter = self.config.sort_by_env
        min_count = self.config.minimum_count

        if not environment_filter or environment_filter == "all":
            counts = dataFrame["OS Name"].value_counts()
            counts = counts[counts >= min_count]
        else:
            counts = (
                dataFrame.groupby(["OS Name", self.vm_data.column_headers["environment"]]).size().unstack().fillna(0)
            )
            counts["total"] = counts.sum(axis=1)
            counts["combined_total"] = counts["prod"] + counts["non-prod"]
            counts = counts[(counts["total"] >= min_count) & (counts["combined_total"] >= min_count)].drop(
                ["total", "combined_total"], axis=1
            )
            counts = counts.sort_values(by="prod", ascending=False)

        return counts

    def get_supported_os_counts(self: t.Self) -> pd.Series:
        data_cp = self.vm_data.create_environment_filtered_dataframe(
            self.config.environments, self.config.environment_filter
        )
        if self.config.environment_filter == "both":
            filtered_counts = (
                data_cp.groupby(["OS Name", self.vm_data.column_headers["environment"]]).size().unstack().fillna(0)
            )
        else:
            filtered_counts = data_cp["OS Name"].value_counts()

        if filtered_counts.empty:
            LOGGER.warning("None found in %s", self.config.environment_filter)
            return pd.Series()

        filtered_counts = filtered_counts[filtered_counts.index.isin(const.SUPPORTED_OSES)]
        filtered_counts = filtered_counts.astype(int)

        return filtered_counts

    def generate_unsupported_os_counts(self: t.Self) -> pd.Series:
        counts = self.vm_data.df["OS Name"].value_counts()

        unsupported_counts = counts[~counts.index.isin(const.SUPPORTED_OSES)]

        other_counts = unsupported_counts[unsupported_counts <= 500]
        other_total = other_counts.sum()
        unsupported_counts = unsupported_counts[unsupported_counts > 500]
        unsupported_counts["Other"] = other_total

        return unsupported_counts

    def get_os_version_distribution(self: t.Self, os_name: str) -> pd.Series:
        df_copy = self.vm_data.df.copy()
        df_copy = df_copy[(df_copy["OS Name"] == os_name)]
        counts = df_copy["OS Version"].fillna("unknown").value_counts().reset_index()
        counts.columns = ["OS Version", "Count"]

        if self.config.minimum_count is not None and self.config.minimum_count > 0:
            counts = counts[counts["Count"] >= self.config.minimum_count]

        return counts

    def by_os(self: t.Self, func: Callable[[str], None]) -> None:
        """Execute func once for each os in get_unique_os_names.

            Func should have one argument (os_name), and return None
        Args:
            func (Callable[[str], None]): Function to execute for each os.
        """
        for os_name in self.get_unique_os_names():
            func(os_name)
