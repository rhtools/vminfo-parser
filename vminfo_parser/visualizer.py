# Std lib imports
import logging
import typing as t
from functools import wraps

# 3rd party imports
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from . import config, const

LOGGER = logging.getLogger(__name__)

V = t.TypeVar("Visualizer", bound="Visualizer")


def plotter(func: t.Callable) -> t.Callable:
    @wraps(func)
    def plot_wrapper(
        v: V,
        data: t.Union[pd.DataFrame, pd.Series],
        *args: t.Optional[str | int],
        **kwargs: t.Optional[str | int],
    ) -> t.Optional[plt.Figure]:
        if data.empty:
            LOGGER.warning("No data to graph")
            return None
        func(v, data, *args, **kwargs)
        figure = plt.gcf()
        if config._IS_TEST:
            return figure

        # TODO: add support for saving to file
        plt.show(block=True)
        plt.close()
        return None

    return plot_wrapper


class Visualizer:
    def __init__(self: t.Self) -> None:
        pass

    @plotter
    def visualize_disk_space_horizontal(
        self: t.Self,
        dataFrame: pd.DataFrame,
    ) -> None:
        """Create horizontal bar chart for disk space

        Args:
            dataFrame (pd.DataFrame): dataframe with Disk Space Counts
        """
        if dataFrame.empty:
            LOGGER.warning("No data to plot")
            return

        # Create a subplot for plotting
        fig, ax = plt.subplots()

        # Plot the sorted counts as a horizontal bar chart

        unique_ranges = dataFrame["Disk Space Range"].value_counts()
        for range, count in unique_ranges.items():
            ax.barh(f"{range}", count)
        # Set titles and labels for the plot
        ax.set_ylabel("Disk Space Range")
        ax.set_xlabel("Number of VMs")
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

        ax.set_title("Hard Drive Space Breakdown for Organization")

    @plotter
    def visualize_disk_space_vertical(
        self: t.Self,
        range_counts_by_environment: pd.DataFrame,
        os_filter: t.Optional[str] = None,
    ) -> None:
        """Create vertical bar chart for disk space

        Args:
            dataFrame (pd.DataFrame): dataframe with Disk Space Counts
            os_filter (t.Optional[str], optional): Name of filter applied to dataFrame for use in plot title. Defaults to None.
        """
        range_counts_by_environment.plot(kind="bar", stacked=False, figsize=(12, 8), rot=45)

        plt.xlabel("Disk Space Range")
        plt.ylabel("Number of VMs")
        plt.title(f'VM Disk Size Ranges Sorted by Environment {f"for {os_filter}" if os_filter else ""}')

    @plotter
    def visualize_os_distribution(
        self: t.Self,
        counts: pd.Series,
        os_names: list[str],
        min_count: int = 500,
    ) -> None:
        """Create horizontal bar chart of OS Counts

        Args:
            counts (pd.Series): series of counts per os
            os_names (list[str]): names of oses in counts
            min_count (int, optional): minimum count of oses graphed for title. Defaults to 500.
        """
        # Define specific colors for identified OS names
        # Generate random colors for bars not in SUPPORTED_OS_COLORS
        random_colors = cm.rainbow(np.linspace(0, 1, len(counts)))
        colors = [const.SUPPORTED_OS_COLORS.get(os, random_colors[i]) for i, os in enumerate(os_names)]

        # Plot the counts as a horizontal bar chart with specified and random colors
        # ax = counts.plot(kind="barh", rot=45, color=colors)
        counts.plot(kind="barh", rot=45, color=colors)

        # Set titles and labels for the plot
        plt.title(f"OS Counts by Environment Type (>= {min_count})")
        plt.xlabel("Count")
        plt.ylabel("Operating Systems")

    @plotter
    def visualize_unsupported_os_distribution(
        self: t.Self,
        counts: pd.Series,
    ) -> None:
        """Create pie chart of unsupported os counts

        Args:
            counts (pd.Series): series of counts per os
        """
        random_colors = cm.rainbow(np.linspace(0, 1, len(counts)))
        plt.pie(
            counts,
            labels=counts.index,
            colors=random_colors,
            autopct="%1.1f%%",
        )
        plt.title("Unsupported Operating System Distribution")

    @plotter
    def visualize_supported_os_distribution(
        self: t.Self,
        counts: pd.Series,
        environment_filter: t.Optional[str] = None,
    ) -> None:
        """Create horizontal bar chart of supported os counts

        Args:
            counts (pd.Series): series of counts per os
            environment_filter (t.Optional[str], optional): environment filter for title. Defaults to None.
        """
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

    @plotter
    def visualize_os_version_distribution(
        self: t.Self,
        dataFrame: pd.DataFrame,
        os_name: str,
    ) -> None:
        """Create horizontal bar chart for os version counts

        Args:
            dataFrame (pd.DataFrame): dataframe of os version counts
            os_name (str): name of os for title
        """
        ax = dataFrame.plot(kind="barh", rot=45)
        plt.title(f"Distribution of {os_name}")
        plt.ylabel("OS Version")
        plt.xlabel("Count")

        plt.xticks(rotation=0)
        ax.set_yticklabels(dataFrame["OS Version"])
