import csv
import glob
import logging
import os
import re
import typing as t
from pathlib import Path

import chardet
import magic
import numpy as np
import pandas as pd

from . import const

LOGGER = logging.getLogger(__name__)


class VMData:
    df: pd.DataFrame
    column_headers: dict[str, str]
    unit_type: str
    normalized: bool

    def __init__(self: t.Self, df: pd.DataFrame, normalize: bool = True) -> None:
        self.df = df
        self.normalized = False

        if normalize:
            self._normalize()
        else:
            self.column_headers = {}
            self.unit_type = ""

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

    @staticmethod
    def _detect_encoding(file_name: str) -> str:
        """
        Attempts to detect the character encoding of a file.
        Useful for handling international CSV files that are not UTF-8

        Args:
            file_name (str): The path to the file

        Returns:
            str: A string with the encoding value
        """
        with open(file_name, "rb") as f:
            rawdata = f.read(10000)
            encoding = chardet.detect(rawdata)
            return encoding["encoding"]

    @staticmethod
    def _detect_delimiter(file_name: str, enconding: str) -> str:
        """
        Attempts to detect the delimiter from a CSV file

        Args:
            file_name (str): The path to the file
            enconding (str): An encoding such as ISO-8859-1 or UTF-8

        Returns:
            str: The delimiter used in the file
        """
        with open(file_name, encoding=enconding) as f:
            sample = f.read(10000)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        return dialect.delimiter

    @classmethod
    def from_file(cls: type[t.Self], filepath: Path, normalize: bool = True) -> t.Self:
        def build_file_list(file_extensions: list, file_type: str) -> list:
            """
            Builds a list of data frames from either excel or csvs (or both).

            Args:
                file_extensions (list): The file extensions to be processed
                file_type (str): Either CSV or Excel file types

            Returns:
                list: A list of pandas dataframes
            """
            temp_list = []
            for ext in file_extensions:
                # find all the files with a given extension
                files = glob.glob(filepath + "/*" + ext)
                for f in files:
                    if file_type == "excel":
                        temp_list.append(pd.read_excel(f))
                    if file_type == "csv":
                        # To ensure proper handling of the CSV files we need to figure out
                        # encoding and delimiters incase they are non-standard
                        encoding = cls._detect_encoding(f)
                        delimiter = cls._detect_delimiter(f, encoding)
                        temp_list.append(pd.read_csv(f, delimiter=delimiter, encoding=encoding))
            return temp_list

        if os.path.isdir(filepath):
            excel_list = build_file_list([".xls", ".xlsx"], "excel")
            csv_list = build_file_list([".csv"], "csv")
            if not excel_list and not csv_list:
                LOGGER.critical("Directory included neither CSV or Excel files")
                exit()
            df = pd.concat((excel_list + csv_list), ignore_index=True)
        else:
            file_type = cls.get_file_type(filepath)
            _, file_extension = os.path.splitext(filepath)
            if file_type == const.MIME["csv"] or file_extension.lower() == ".csv":
                if os.stat(filepath).st_size != 0:
                    encoding = cls._detect_encoding(filepath)
                    delimiter = cls._detect_delimiter(filepath, encoding)
                    df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
                else:
                    LOGGER.critical("File passed in was neither a CSV nor an Excel file")
                    exit()
            elif file_type in const.MIME["excel"]:
                df = pd.read_excel(filepath)
            else:
                LOGGER.critical("File passed in was neither a CSV nor an Excel file")
                exit()
        return cls(df, normalize)

    def _set_column_headings(self: t.Self) -> None:
        """
        Sets the column headings based on the versions defined in const.COLUMN_HEADERS.

        Returns:
            None

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

        LOGGER.debug(f"Using VERSION_{best_match} as the closest match.")

        self.column_headers = const.COLUMN_HEADERS[best_match].copy()
        self.unit_type = "GiB" if best_match == "VERSION_1" else "MiB"

        missing_headers = [header for header in self.column_headers.values() if header not in self.df.columns]
        if self.column_headers["environment"] in missing_headers:
            LOGGER.warning(
                "Environment heading %s is missing. Inserting empty column so program can continue"
                % self.column_headers["environment"]
            )
            self.df[self.column_headers["environment"]] = ""
            # We want to remove the environment header from the list so that any remaining headers are still
            # caught as missing
            missing_headers.remove(self.column_headers["environment"])
        if missing_headers:
            LOGGER.critical("The following headers are missing: %s", missing_headers)
            exit()

    def _set_os_columns(self: t.Self) -> None:
        """
        Add os name and version columns to dataframe.

        Checks to see if output columns exist in dataframe and returns if so.

        Returns:
            None
        """
        if all(col in self.df.columns for col in const.EXTRA_COLUMNS_DEST):
            LOGGER.info("All columns already exist")
            return None

        primary_os_column = self.column_headers.get("operatingSystemFromVMTools")
        secondary_os_column = self.column_headers.get("operatingSystemFromVMConfig")

        combined_os: pd.Series = self.df[primary_os_column].fillna(self.df[secondary_os_column])

        # Set "OS Name", "OS Version", "Architecture" with regex match of combined_os
        self.df[const.EXTRA_COLUMNS_DEST] = (
            # Parse as None Windows OS
            combined_os.str.extract(const.EXTRA_COLUMNS_NON_WINDOWS_REGEX)
            # If no match, parse as Windows Server
            .fillna(combined_os.str.extract(const.EXTRA_COLUMNS_WINDOWS_SERVER_REGEX))
            # If no match, parse as Windows Desktop
            .fillna(combined_os.str.extract(const.EXTRA_COLUMNS_WINDOWS_DESKTOP_REGEX, flags=re.IGNORECASE))
        )

        # if No OS Name after regex,  set original value as OS Name
        self.df[const.EXTRA_COLUMNS_DEST[0]] = self.df[const.EXTRA_COLUMNS_DEST[0]].fillna(combined_os)

    def _normalize_to_GiB(self: t.Self) -> None:
        """Set disk and Memory to GiB if Mib

        Args:
            self (t.Self): _description_

        Raises:
            ValueError: _description_
        """
        # Get the column names from the column_headers dictionary
        memory_col = self.column_headers["vmMemory"]
        disk_col = self.column_headers["vmDisk"]
        unit_type = self.unit_type

        if unit_type == "MiB":
            # If the disk and ram are in GiB, convert to GiB
            # In addition, some columns may have numbers like '123 456'
            # get rid of that white space
            cleaned_memory_column = pd.to_numeric(
                self.df[memory_col].astype(str).str.replace(r"\s+", "", regex=True), errors="coerce"
            )
            cleaned_disk_column = pd.to_numeric(
                self.df[disk_col].astype(str).str.replace(r"\s+", "", regex=True), errors="coerce"
            )
            self.df[memory_col] = np.ceil(cleaned_memory_column / 1024).astype(int)
            self.df[disk_col] = np.ceil(cleaned_disk_column / 1024).astype(int)
            self.unit_type = "GiB"
        elif unit_type != "GiB":
            raise ValueError(f"Unexpected unit type: {unit_type}")

    def _normalize(self: t.Self) -> None:
        """Set instance vars and format data to match expectations.

        Args:
            self (t.Self): _description_
        """

        self._set_column_headings()
        self._set_os_columns()
        self._normalize_to_GiB()
        self.normalized = True

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
        if "Site Name" not in new_site_df.columns:
            raise ValueError('\n\n\n-------> Error: The "Site Name" column does not exist in the DataFrame. <------')
        # Check if all site-specific columns already exist
        if all(col in new_site_df.columns for col in site_columns):
            raise ValueError("Site-specific columns already exist in the DataFrame.")

        # Get the column names from the column_headers dictionary
        memory_col = self.column_headers["vmMemory"]
        disk_col = self.column_headers["vmDisk"]
        cpu_col = self.column_headers["vCPU"]

        new_site_df[disk_col] = np.ceil(new_site_df[disk_col] / 1024).astype(int)

        # Group by Site Name and calculate sums
        site_usage = new_site_df.groupby("Site Name")[[memory_col, disk_col, cpu_col]].sum().reset_index()
        site_usage["Site_VM_Count"] = new_site_df.groupby("Site Name")["Site Name"].count().values

        # Rename columns to match the desired output
        site_usage.columns = ["Site Name"] + site_columns

        return site_usage

    def create_environment_filtered_dataframe(
        self: t.Self, prod_envs: list[str], env_filter: str | None = None
    ) -> pd.DataFrame:
        """Create copy of dataframe, with environment column replaced with category, and filtered by requested filter

        Args:
            prod_envs (list[str]): list of environment labels defined as prod. (all other labels will be non-prod)
            env_filter (str | None, optional): filter to apply to environment column. Defaults to None.

        Returns:
            pd.DataFrame: dataframe filtered by env_filter with modified environment column
        """
        data_cp = self.df.copy()
        data_cp[self.column_headers["environment"]] = self.df[self.column_headers["environment"]].apply(
            _categorize_environment, prod_envs=prod_envs
        )

        if env_filter and env_filter not in ["all", "both"]:
            data_cp = data_cp[data_cp[self.column_headers["environment"]] == env_filter]

        return data_cp

    def save_to_csv(self: t.Self, path: str) -> None:
        self.df.to_csv(path, index=False)


def _categorize_environment(x: str, prod_envs: list[str]) -> str:
    """Categorize environment value based on configured prod environment labels

    Args:
        x (str): environment value to compare, passed by pandas when using per row operations
        prod_envs (list[str]): list of environment labels to define as prod

    Returns:
        str: environment category, one of ["non-prod", "prod", "all envs"]
    """
    if pd.isnull(x):
        return "non-prod"

    if not prod_envs:
        return "all envs"

    # Ensure x is a string
    if isinstance(x, str):
        for env in prod_envs:
            if env in x:
                return "prod"

    return "non-prod"
