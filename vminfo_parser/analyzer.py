# Std lib imports
import logging
import typing as t
from collections.abc import Callable

# 3rd party imports
import pandas as pd

from . import const
from .config import Config
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

    def generate_dynamic_ranges(self: t.Self, max_disk_space: int) -> list[tuple[int, int]]:
        """
        Generate dynamic disk space ranges based on the maximum disk space and specified display options.
        This function returns a list of tuples representing the ranges of disk space in either terabytes or gigabytes.

        Args:
            max_disk_space (int): The maximum disk space to consider for generating ranges.

        Returns:
            list: A list of tuples representing the dynamic disk space ranges.

        Examples:
            >>> generate_dynamic_ranges(150000)
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
        if self.config.breakdown_by_terabyte:
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
        elif self.config.over_under_tb:
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
    ) -> list[tuple[int, int]]:
        """
        Calculate the ranges of disk space based on the provided DataFrame and specified display options.
        This function processes the DataFrame to determine which disk space ranges contain virtual machines.

        Args:
            dataFrame (pd.DataFrame, optional): The DataFrame containing disk space data.
                If None, the default DataFrame from the instance will be used. Defaults to None.

        Returns:
            list[tuple[int, int]]: A list of tuples representing the disk space ranges that contain virtual machines.

        Examples:
            >>> calculate_disk_space_ranges(dataFrame=my_dataframe)
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
        disk_space_ranges = self.generate_dynamic_ranges(max_disk_space)
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
        disk_space_ranges = self.calculate_disk_space_ranges(dataFrame=df)

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
            list[str]: A list of unique OS Names
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
                return [self.config.os_name]
            return []
        return os_names

    def get_operating_system_counts(self: t.Self) -> pd.Series | pd.DataFrame:
        """Returns the counts of operating systems based on the configured environment filter.

        This function calculates the counts of operating systems and returns the results.

        Args:
            None
        Returns:
            pd.Series | pd.DataFrame: Series object containing counts, indexed by OS, or
              DataFrame object containing counts per environment category, indexed by OS
        """
        df = self.vm_data.create_environment_filtered_dataframe(
            self.config.environments, env_filter=self.config.environment_filter
        )

        if self.config.os_name:
            df = df[df["OS Name"] == self.config.os_name]

        return self._calculate_os_counts(df)

    def _calculate_os_counts(self: t.Self, dataFrame: pd.DataFrame | None = None) -> pd.Series | pd.DataFrame:
        """Calculates the counts of operating systems based on the provided environment filter.

        This function analyzes the DataFrame to count occurrences of operating systems, applying filters as necessary.
        It returns the counts and the corresponding operating system names, allowing for further processing
        or visualization.

        Args:
            dataFrame (pd.DataFrame, optional): The DataFrame containing the data to analyze. Defaults to None.
        Returns:
            pd.Series | pd.DataFrame: Series object containing counts, indexed by OS, or
              DataFrame object containing counts per environment category, indexed by OS
        """
        if dataFrame is None:
            dataFrame = self.vm_data.create_environment_filtered_dataframe(
                self.config.environments, env_filter=self.config.environment_filter
            )

        if self.config.environment_filter == "both":
            # create Series of counts by "OS Name" and "environment"
            # example:
            #   OS Name   Environment
            #   CentOS    non-prod         138
            #             prod             454

            counts_raw: pd.Series[int] = dataFrame.groupby(
                ["OS Name", self.vm_data.column_headers["environment"]]
            ).size()
            # convert Series back into DataFrame
            # example:
            #   Environment                                         non-prod     prod
            #   OS Name
            #   CentOS                                                 138.0    454.0
            counts: pd.DataFrame = counts_raw.unstack().fillna(0)

            # add total column to counts DataFrame to use for filters and sorting
            counts["total"] = counts.sum(axis=1)
            # sort by total counts
            counts: pd.DataFrame = counts.sort_values(by="total", ascending=False)

            # implement minimum count filtering
            if self.config.count_filter:
                # create DataFrame of counts less than count_filter
                other_counts: pd.DataFrame = counts[counts["total"] < self.config.count_filter]
                # if only one entry below count_fiter,  dont filter it
                if len(other_counts) > 1:
                    # sum other_counts by column
                    other_sum: pd.Series = other_counts.sum()
                    # remove counts below minimum from counts dataframe
                    counts = counts[counts["total"] >= self.config.count_filter]
                    # sort by total
                    # before other is readded
                    counts = counts.sort_values(by="total", ascending=False)
                    # transpose counts for addition of Other
                    counts = counts.T
                    # Add other_sum as column
                    counts["Other"] = other_sum
                    # reverse transpose
                    counts = counts.T

            counts = counts.drop("total", axis=1)

        else:
            # create a Series of sorted integers (counts) from index "OS Name" in dataframe
            counts: pd.Series[int] = dataFrame["OS Name"].value_counts()

            # implement minimum count filtering
            if self.config.count_filter:
                # create series of counts less than count_filter
                other_counts: pd.Series[int] = counts[counts < self.config.count_filter]
                # if only one entry below count_fiter,  dont filter it
                if len(other_counts) > 1:
                    # total of all counts below minimum
                    other_total = other_counts.sum()
                    # remove counts below minimum from counts series
                    counts = counts[counts >= self.config.count_filter]
                    # add new entry in series with a name of "Other" and total of all removed entries
                    counts["Other"] = other_total

        return counts.astype(int)

    def get_supported_os_counts(self: t.Self) -> pd.Series | pd.DataFrame:
        """Returns the counts of supported operating systems based on the configured environment filter.

        This function calculates the counts of supported operating systems and returns the results.

        Args:
            None
        Returns:
            pd.Series | pd.DataFrame: Series object containing counts, indexed by OS, or
              DataFrame object containing counts per environment category, indexed by OS
        """

        dataFrame = self.vm_data.create_environment_filtered_dataframe(
            self.config.environments, env_filter=self.config.environment_filter
        )

        dataFrame = dataFrame[dataFrame["OS Name"].isin(const.SUPPORTED_OSES)]

        return self._calculate_os_counts(dataFrame)

    def get_unsupported_os_counts(self: t.Self) -> pd.Series | pd.DataFrame:
        """Returns the counts of supported operating systems based on the configured environment filter.

        This function calculates the counts of supported operating systems and returns the results.

        Args:
            None
        Returns:
            pd.Series | pd.DataFrame: Series object containing counts, indexed by OS, or
              DataFrame object containing counts per environment category, indexed by OS
        """

        dataFrame = self.vm_data.create_environment_filtered_dataframe(
            self.config.environments, env_filter=self.config.environment_filter
        )

        dataFrame = dataFrame[~dataFrame["OS Name"].isin(const.SUPPORTED_OSES)]

        return self._calculate_os_counts(dataFrame)

    def get_os_version_distribution(self: t.Self, os_name: str) -> pd.DataFrame:
        """Create Dataframe of Counts by OS Version for a given OS.

        Args:
            os_name (str): Name of OS to count versions

        Returns:
            pd.DataFrame: Dataframe with 2 columns, one labeled "OS Version", and the other labeled "Count"
        """
        df_copy = self.vm_data.df.copy()
        df_copy = df_copy[(df_copy["OS Name"] == os_name)]
        counts = df_copy["OS Version"].fillna("unknown").value_counts().reset_index()
        counts.columns = ["OS Version", "Count"]

        if self.config.count_filter:
            counts = counts[counts["Count"] >= self.config.count_filter]

        return counts

    def by_os(self: t.Self, func: Callable[[str], None]) -> None:
        """Execute func once for each os in get_unique_os_names.

            Func should have one argument (os_name), and return None
        Args:
            func (Callable[[str], None]): Function to execute for each os.
        """
        for os_name in self.get_unique_os_names():
            func(os_name)
