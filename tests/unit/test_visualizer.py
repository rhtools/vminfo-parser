import logging

import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt

from vminfo_parser import const as vm_const
from vminfo_parser.visualizer import Visualizer, plotter


@pytest.fixture
def disk_range_counts_df() -> pd.DataFrame:
    return pd.DataFrame(
        index=pd.Index(
            [
                "0-200 GiB",
                "201-400 GiB",
                "401-600 GiB",
                "601-900 GiB",
                "901-1500 GiB",
                "1501-2000 GiB",
                "2001-3000 GiB",
                "3001-5000 GiB",
                "5001-9000 GiB",
                "9001-114256 GiB",
            ],
            dtype="object",
            name="Disk Space Range",
        ),
        columns=pd.Index(["non-prod", "prod"], dtype="object", name="Environment"),
        data=np.array(
            [
                [2312, 5082],
                [6176, 12970],
                [3338, 5232],
                [1828, 6744],
                [1039, 3580],
                [253, 658],
                [1398, 915],
                [338, 821],
                [131, 1006],
                [65, 707],
            ]
        ),
    )


@pytest.fixture
def supported_os_count_series() -> pd.Series:
    return pd.Series(
        index=pd.Index(sorted(vm_const.SUPPORTED_OSES), dtype=object, name="OS Name"),
        data=np.array([724, 837, 925, 519]),
    )


@pytest.fixture
def unsupported_os_count_series() -> pd.Series:
    return pd.Series(
        index=pd.Index(["Ubuntu", "Other Linux", "TESTOS"], dtype=object, name="OS Name"), data=np.array([56, 132, 848])
    )


@pytest.fixture
def all_os_count_series(supported_os_count_series: pd.Series, unsupported_os_count_series: pd.Series) -> pd.Series:
    return pd.concat([supported_os_count_series, unsupported_os_count_series])


@pytest.mark.mpl_image_compare(savefig_kwargs={"bbox_inches": "tight"})
def test_plotter(visualizer: Visualizer) -> plt.Figure:
    @plotter
    def simpleplot(self: Visualizer, dataframe: pd.DataFrame) -> None:
        dataframe.plot(kind="bar")
        plt.title("Test Title")

    figure = simpleplot(visualizer, pd.DataFrame(zip(range(5), range(5))))
    assert isinstance(figure, plt.Figure)
    return figure


def test_plotter_empty(visualizer: Visualizer, caplog: pytest.LogCaptureFixture) -> None:
    @plotter
    def simpleplot(self: Visualizer, dataframe: pd.DataFrame) -> None:
        raise RuntimeError("This shouldn't be called")

    figure = simpleplot(visualizer, pd.DataFrame())
    assert figure is None
    assert caplog.record_tuples == [("vminfo_parser.visualizer", logging.WARNING, "No data to graph")]


@pytest.mark.mpl_image_compare(savefig_kwargs={"bbox_inches": "tight"})
def test_visualize_disk_space_vertical(visualizer: Visualizer, disk_range_counts_df: pd.DataFrame) -> plt.Figure:
    return visualizer.visualize_disk_space_vertical(disk_range_counts_df)


@pytest.mark.mpl_image_compare(savefig_kwargs={"bbox_inches": "tight"})
def test_visualize_disk_space_horizontal(visualizer: Visualizer, disk_range_counts_df: pd.DataFrame) -> plt.Figure:
    return visualizer.visualize_disk_space_horizontal(disk_range_counts_df)


@pytest.mark.mpl_image_compare(savefig_kwargs={"bbox_inches": "tight"})
def test_visualize_os_distribution(visualizer: Visualizer, all_os_count_series: pd.Series) -> plt.Figure:
    sorted_series = all_os_count_series[all_os_count_series >= 100].sort_values(ascending=False)
    return visualizer.visualize_os_distribution(
        sorted_series,
        min_count=100,
    )


@pytest.mark.mpl_image_compare(savefig_kwargs={"bbox_inches": "tight"})
def test_visualize_unsupported_os_distribution(
    visualizer: Visualizer, unsupported_os_count_series: pd.Series
) -> plt.Figure:
    return visualizer.visualize_unsupported_os_distribution(unsupported_os_count_series)


@pytest.mark.mpl_image_compare(savefig_kwargs={"bbox_inches": "tight"})
def test_visualize_supported_os_distribution(
    visualizer: Visualizer, supported_os_count_series: pd.Series
) -> plt.Figure:
    return visualizer.visualize_supported_os_distribution(supported_os_count_series)
