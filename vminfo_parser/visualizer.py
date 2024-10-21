import logging
import math
import typing as t
from collections.abc import Callable, Iterable

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from matplotlib import colormaps
from matplotlib.figure import Figure
from matplotlib.typing import ColorType

from . import config, const

LOGGER = logging.getLogger(__name__)


# Parameter Specification for methods that use the plotter decorator
# NOTE: VSCode Pylance extention does not properly display type hints for ParamSpec
#       but it didnt handle functools.wraps properly either, so no loss by switching to new standard
PlotterParam = t.ParamSpec("PlotterParam")


def plotter(func: Callable[PlotterParam, None]) -> Callable[PlotterParam, Figure | None]:
    """Decorate functions that use matplotlib.pyplot to create graphs.

    Allows for different output methods depending on external variables.
    Currently only implemented option is returning the figure in testing, and showing the figure interactively.

    Args:
        func (Callable[PlotterParam, None]): Function or Method being wrapped

    Returns:
        Callable[PlotterParam, Figure] | None: Wrapped Funciton or Method
    """

    def plot_wrapper(
        *args: PlotterParam.args,
        **kwargs: PlotterParam.kwargs,
    ) -> Figure | None:
        """Wrap plotter fuction to enable configured output.

        Returns:
            plt.Figure | None: Figure from current matplotlib canvas if in testing. Defaults to None
        """
        data: pd.DataFrame | pd.Series | None = None
        for arg in args:
            if isinstance(arg, pd.DataFrame | pd.Series):
                data = arg
                break
        else:
            for value in kwargs.values():
                if isinstance(value, pd.DataFrame | pd.Series):
                    data = value
                    break

        if data is None or data.empty:
            LOGGER.warning("No data to graph")
            return None
        func(*args, **kwargs)
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
        """Create horizontal bar chart for disk space.

        Args:
            dataFrame (pd.DataFrame): dataframe with Disk Space Counts
        """
        # Create a subplot for plotting
        fig, ax = plt.subplots()

        df = dataFrame.copy()
        if len(df.axes) == 2:
            df = df.sum(axis=1)

        # Plot the sorted counts as a horizontal bar chart

        for range, count in df.items():
            ax.barh(f"{range}", count)

        # Set titles and labels for the plot
        plt.ylabel("Disk Space Range")
        plt.xlabel("Number of VMs")
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

        plt.title("Hard Drive Space Breakdown for Organization")

    @plotter
    def visualize_disk_space_vertical(
        self: t.Self,
        range_counts_by_environment: pd.DataFrame,
        os_filter: str | None = None,
    ) -> None:
        """Create vertical bar chart for disk space.

        Args:
            dataFrame (pd.DataFrame): dataframe with Disk Space Counts
            os_filter (str | None, optional): Name of filter applied to dataFrame for use in plot title. Defaults to None.
        """
        range_counts_by_environment.plot(kind="bar", stacked=False, figsize=(12, 8), rot=45)

        plt.xlabel("Disk Space Range")
        plt.ylabel("Number of VMs")
        plt.title(f'VM Disk Size Ranges Sorted by Environment {f"for {os_filter}" if os_filter else ""}')

    @plotter
    def visualize_os_distribution(
        self: t.Self,
        counts: pd.Series,
        min_count: int = 500,
    ) -> None:
        """Create horizontal bar chart of OS Counts.

        Args:
            counts (pd.Series): series of counts per os
            min_count (int, optional): minimum count of oses graphed for title. Defaults to 500.
        """
        # this may not be needed anymore, it might be simplifiable to counts.index
        os_names: list[str] = [idx[1] for idx in counts.index] if counts.index.nlevels == 2 else counts.index
        # Plot the counts as a horizontal bar chart with specified and random colors
        counts.plot(kind="barh", rot=45, color=_get_colors(os_names))

        # Set titles and labels for the plot
        plt.title(f"OS Counts by Environment Type (>= {min_count})")
        plt.xlabel("Count")
        plt.ylabel("Operating Systems")

    @plotter
    def visualize_unsupported_os_distribution(
        self: t.Self,
        counts: pd.Series,
    ) -> None:
        """Create pie chart of unsupported os counts.

        Args:
            counts (pd.Series): series of counts per os
        """
        random_colors = colormaps["rainbow"](np.linspace(0, 1, len(counts)))
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
        environment_filter: str | None = None,
    ) -> None:
        """Create horizontal bar chart of supported os counts.

        Args:
            counts (pd.Series): series of counts per os
            environment_filter (str | None, optional): environment filter for title. Defaults to None.
        """
        colors = [const.SUPPORTED_OS_COLORS[os] for os in counts.index]

        if not environment_filter or environment_filter != "both":
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
        """Create horizontal bar chart for os version counts.

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


def _get_colors(os_names: list[str]) -> list[ColorType]:
    """Generate Colors for OS names of mixed support status.

    Uses np.linspace to generate equally spaced colors, then removes the colors closest
    to the predefined supported os colors.  returns a list with predifined and generated colors ordered by os_names arg

    Args:
        os_names (list[str]): list of os names

    Returns:
        list[ColorType]: matplotlib colors for each os.
    """
    supported_os_names = list(set(os_names).intersection(const.SUPPORTED_OSES))
    supported_os_colors: list[ColorType] = [mcolors.to_rgba(const.SUPPORTED_OS_COLORS[os]) for os in supported_os_names]
    raw_colors: list[ColorType] = colormaps["rainbow"](
        np.linspace(0, 1, len(os_names)),
    ).tolist()
    color_diff: list[float] = [4.0 for _ in raw_colors]

    for idx, rawcolor in enumerate(raw_colors):
        diff: float = 4.0  # Max possible value
        for usedcolor in supported_os_colors:
            new_diff = _color_diff(usedcolor, rawcolor)
            diff = new_diff if new_diff < diff else diff
        color_diff[idx] = diff

    for _ in range(len(supported_os_colors)):
        idx = color_diff.index(min(color_diff))
        del raw_colors[idx]
        del color_diff[idx]

    chosen_colors: list[ColorType] = []
    for os in os_names:
        if os in supported_os_names:
            chosen_colors.append(mcolors.to_rgba(const.SUPPORTED_OS_COLORS[os]))
        else:
            chosen_colors.append(raw_colors.pop())
    return chosen_colors


def _color_diff(color_a: ColorType, color_b: ColorType) -> float:
    """Calculate absolute value of the distance between two colors.

    Args:
        a (ColorType): color to calculate difference
        b (ColorType): color to calculate difference

    Returns:
        float: absolute value of the distance between a and b in rgba color space
    """
    color_tuples = (mcolors.to_rgba(color_a), mcolors.to_rgba(color_b))
    color_values: Iterable[tuple[float, float]] = zip(*color_tuples)
    return math.fsum([abs(a - b) for a, b in color_values])
