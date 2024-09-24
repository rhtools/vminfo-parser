# Std lib imports
import logging
import typing as t

# 3rd party imports
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from . import const
from .config import Config

LOGGER = logging.getLogger(__name__)


class Visualizer:
    def __init__(self: t.Self) -> None:
        pass

    @classmethod
    def visualize_disk_space(
        cls: t.Self,
        disk_space_ranges: t.Optional[list[tuple[int, int]]],
        dataFrame: pd.DataFrame,
        column_headers: t.Optional[dict[str, str]],
    ) -> None:

        # Count the number of VMs in each disk space range
        range_counts = {range_: 0 for range_ in disk_space_ranges}
        for lower, upper in disk_space_ranges:
            mask = (dataFrame[column_headers["vmDisk"]] >= lower) & (dataFrame[column_headers["vmDisk"]] <= upper)
            count = dataFrame.loc[mask].shape[0]
            range_counts[(lower, upper)] = count

        # Sort the counts and plot them as a horizontal bar chart
        sorted_dict = dict(sorted(range_counts.items(), key=lambda x: x[1]))

        if dataFrame.empty:
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
        dataFrame: pd.DataFrame,
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

        if dataFrame.empty:
            LOGGER.warning("No data to plot")
            return

        # Set titles and labels for the plot
        plt.title(f"OS Counts by Environment Type (>= {min_count})")
        plt.xlabel("Count")
        plt.ylabel("Operating Systems")

        # Display the plot
        plt.show(block=True)
        plt.close()

    def visualize_unsupported_os_distribution(self: t.Self, unsupported_counts: pd.Series) -> None:

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

    def visualize_os_version_distribution(
        self: t.Self, os_name: str, dataFrame: pd.DataFrame, config: Config, counts_dataframe: pd.DataFrame
    ) -> None:
        if not counts_dataframe.empty:
            ax = counts_dataframe.plot(kind="barh", rot=45)
            plt.title(f"Distribution of {os_name}")
            plt.ylabel("OS Version")
            plt.xlabel("Count")

            plt.xticks(rotation=0)
            ax.set_yticklabels(counts_dataframe["OS Version"])

            plt.show(block=True)
            plt.close()
