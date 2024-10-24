import logging
import re
import typing as t
from pathlib import Path

import magic
import numpy as np
import pandas as pd

from . import const

LOGGER = logging.getLogger(__name__)


class VMData:
    def __init__(self: t.Self, df: pd.DataFrame) -> None:
        self.df: pd.DataFrame = df
        self.column_headers: dict[str, str] = {}

    @staticmethod
    def get_file_type(filepath: Path) -> str:
        """
        Returns the MIME type of the file located at the specified file path.

        Args:
            file_path (str): The path to the file for which the MIME type should be determined.

        Returns:
            str: The MIME type of the file.

        Raises:
            FileNotFoundError: If the file at the specified file path does not exist.
        """
        mime_type = magic.from_file(filepath, mime=True)
        return mime_type

    @classmethod
    def from_file(cls: type[t.Self], filepath: Path) -> t.Self:
        file_type = cls.get_file_type(filepath)
        if file_type == const.MIME.get("csv"):
            df = pd.read_csv(filepath)
        elif file_type in const.MIME.get("excel"):
            df = pd.read_excel(filepath)
        else:
            LOGGER.critical("File passed in was neither a CSV nor an Excel file")
            exit()
        return cls(df)

    def set_column_headings(self: t.Self) -> None:
        """
        Sets the column headings based on the versions defined in const.COLUMN_HEADERS.
        Raises:
            ValueError: If no matching header set is found.
        """
        best_match = None
        max_matches = 0

        for version, headers in const.COLUMN_HEADERS.items():
            matches = 0
            for header in headers.values():
                if header in self.df.columns:
                    matches += 1
            if matches > max_matches:
                max_matches = matches
                best_match = version

        if best_match is None:
            raise ValueError("No matching header set found")

        self.column_headers = const.COLUMN_HEADERS[best_match].copy()
        missing_headers = [header for header in self.column_headers.values() if header not in self.df.columns]
        self.column_headers["unitType"] = "GB" if best_match == "VERSION_1" else "MB"

        LOGGER.debug(f"Using VERSION_{best_match} as the closest match.")

        if missing_headers:
            LOGGER.critical("The following headers are missing: %s", missing_headers)
            exit()

    def add_extra_columns(self: t.Self) -> None:
        primary_os_column = self.column_headers.get("operatingSystemFromVMTools")
        secondary_os_column = self.column_headers.get("operatingSystemFromVMConfig")

        combined_os_column = "combined_operating_system"
        self.df[combined_os_column] = self.df[secondary_os_column].where(
            self.df[primary_os_column].isnull(), self.df[primary_os_column]
        )

        if not all(col in self.df.columns for col in const.EXTRA_COLUMNS_DEST):
            self.df[const.EXTRA_COLUMNS_DEST] = self.df[combined_os_column].str.extract(
                const.EXTRA_COLUMNS_NON_WINDOWS_REGEX
            )
            self.df[const.EXTRA_WINDOWS_SERVER_COLUMNS] = self.df[combined_os_column].str.extract(
                const.EXTRA_COLUMNS_WINDOWS_SERVER_REGEX
            )
            self.df[const.EXTRA_WINDOWS_DESKTOP_COLUMNS] = self.df[combined_os_column].str.extract(
                const.EXTRA_COLUMNS_WINDOWS_DESKTOP_REGEX, flags=re.IGNORECASE
            )

            for idx, column in enumerate(const.EXTRA_COLUMNS_DEST):
                self.df[column] = self.df[const.EXTRA_WINDOWS_SERVER_COLUMNS[idx]].where(
                    self.df[column].isnull(), self.df[column]
                )
                self.df[column] = self.df[const.EXTRA_WINDOWS_DESKTOP_COLUMNS[idx]].where(
                    self.df[column].isnull(), self.df[column]
                )
            self.df[const.EXTRA_COLUMNS_DEST[0]] = self.df[combined_os_column].where(
                self.df[const.EXTRA_COLUMNS_DEST[0]].isnull(),
                self.df[const.EXTRA_COLUMNS_DEST[0]],
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
            pd.DataFrame: A DataFrame containing the aggregated resource usage for each site, with renamed
                          columns for clarity.

        Examples:
            site_usage_df = create_site_specific_dataframe()
        """
        site_columns = ["Site_RAM_Usage", "Site_Disk_Usage", "Site_CPU_Usage", "Site_VM_Count"]
        new_site_df = self.df.copy()
        # Check if all site-specific columns already exist
        if all(col in new_site_df.columns for col in site_columns):
            raise ValueError("Site-specific columns already exist in the DataFrame.")

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
