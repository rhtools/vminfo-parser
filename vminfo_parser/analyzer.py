# Std lib imports
import logging
import typing as t

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
        column_headers: t.Optional[dict[str, str]] = None,
    ) -> None:
        self.vm_data = vm_data
        self.config = config
        self.column_headers = column_headers if column_headers else vm_data.column_headers
        self.visualizer = Visualizer()
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

        # Normalize the Disk Column to GiB before applying further analysis
        if self.column_headers["unitType"] == "MB":
            dataFrame[frameHeading] = dataFrame[frameHeading] / 1024
        min_disk_space = round(int(dataFrame[frameHeading].min()))
        max_disk_space = round(int(dataFrame[frameHeading].max()))

        disk_space_ranges_dict = {
            "tb": [
                (min_disk_space, 2000),
                (2001, 10000),
                (10001, 20000),
                (20001, 50000),
                (50001, 100000),
                (100001, max_disk_space),
            ],
            "gb": [
                (min_disk_space, 200),
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
            disk_space_ranges = [(min_disk_space, 1000), (1001, max_disk_space)]
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

        disk_space_ranges_with_vms = []
        for range_start, range_end in disk_space_ranges:
            epsilon = 1

            vms_in_range = dataFrame[
                (dataFrame[frameHeading] >= range_start - epsilon) & (dataFrame[frameHeading] <= range_end + epsilon)
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
        # This copy has a paired down version of the information and then environments have been changed to
        # prod/non-prod
        diskHeading = self.column_headers["vmDisk"]
        envHeading = self.column_headers["environment"]

        disk_space_ranges = self.calculate_disk_space_ranges(
            dataFrame=dataFrame,
            show_disk_in_tb=show_disk_in_tb,
            over_under_tb=over_under_tb,
        )

        for lower, upper in disk_space_ranges:
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

        # create an integer of the large end of range for sorting by size of range
        range_counts_by_environment["second_number"] = (
            range_counts_by_environment.index.str.split("-").str[1].str.split().str[0].astype(int)
        )
        sorted_range_counts_by_environment = range_counts_by_environment.sort_values(by="second_number", ascending=True)
        sorted_range_counts_by_environment.drop("second_number", axis=1, inplace=True)

        # Apply the conversion to the index
        sorted_range_counts_by_environment.index = sorted_range_counts_by_environment.index.map(self.convert_to_tb)

        # Now call the print_formatted_disk_space method
        self.cli_output.print_formatted_disk_space(
            sorted_range_counts_by_environment,
            environment_filter,
            env_keywords,
            os_filter=os_filter,
        )

        # Call the new visualize method
        if self.config.generate_graphs:
            if environment_filter == "all":
                self.visualizer.visualize_disk_space_horizontal(sorted_range_counts_by_environment)
            else:
                self.visualizer.visualize_disk_space_vertical(
                    sorted_range_counts_by_environment,
                    os_filter=os_filter,
                )

    def handle_operating_system_counts(self: t.Self, environment_filter: str, dataFrame: pd.DataFrame = None) -> None:
        """Handles the counting of operating systems based on the provided environment filter.

        This function calculates the counts of operating systems and outputs the results.
        It also visualizes the distribution of operating systems if the configuration allows for it.

        Args:
            environment_filter (str): A filter to apply when counting operating systems.
            dataFrame (pd.DataFrame, optional): A DataFrame containing relevant data. Defaults to None.

        Returns:
            None
        """
        # Set the minimum count to what the user inputs
        # If that is empty set the minmum to None
        min_count = getattr(self.config, "minimum_count", None)
        counts, os_names = self._calculate_os_counts(environment_filter, dataFrame, min_count)

        self.cli_output.format_series_output(counts)

        if self.config.generate_graphs:
            self.visualizer.visualize_os_distribution(counts, os_names, min_count)

    def _calculate_os_counts(
        self: t.Self, environment_filter: str, dataFrame: pd.DataFrame = None, min_count: int = None
    ) -> tuple[pd.Series, list[str]]:
        """Calculates the counts of operating systems based on the provided environment filter.

        This function analyzes the DataFrame to count occurrences of operating systems, applying filters as necessary.
        It returns the counts and the corresponding operating system names, allowing for further processing
        or visualization.

        Args:
            environment_filter (str): The filter to apply when counting operating systems.
            dataFrame (pd.DataFrame, optional): The DataFrame containing the data to analyze. Defaults to None.
            min_count (int, optional): The minimum count threshold for including operating systems. Defaults to None.

        Returns:
            tuple[pd.Series, list[str]]: A tuple containing a Series of counts and a list of operating system names.
        """
        if dataFrame is None:
            dataFrame = self.vm_data.df

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

    def generate_supported_os_counts(
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

        return filtered_counts

    def generate_unsupported_os_counts(self: t.Self) -> pd.Series:
        counts = self.vm_data.df["OS Name"].value_counts()

        unsupported_counts = counts[~counts.index.isin(const.SUPPORTED_OSES)]

        other_counts = unsupported_counts[unsupported_counts <= 500]
        other_total = other_counts.sum()
        unsupported_counts = unsupported_counts[unsupported_counts > 500]
        unsupported_counts["Other"] = other_total

        return unsupported_counts

    def generate_os_version_distribution(
        self: t.Self, dataFrame: pd.DataFrame, os_name: str, minimum_count: int
    ) -> pd.DataFrame:

        filtered_df = dataFrame[(dataFrame["OS Name"] == os_name)]
        counts = filtered_df["OS Version"].fillna("unknown").value_counts().reset_index()
        counts.columns = ["OS Version", "Count"]

        if minimum_count is not None and minimum_count > 0:
            counts = counts[counts["Count"] >= minimum_count]

        return counts

    def sort_attribute_by_environment(
        self: t.Self,
        *env_keywords: str,
        attribute: str = "operatingSystem",
        os_filter: t.Optional[str] = None,
        environment_filter: t.Optional[str] = None,
        show_disk_in_tb: bool = False,
        over_under_tb: bool = False,
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
