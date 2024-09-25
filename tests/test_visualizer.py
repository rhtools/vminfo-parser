import logging

import numpy as np
import pandas as pd
import pytest
from matplotlib import pyplot as plt

from vminfo_parser.visualizer import Visualizer, plotter


@pytest.mark.mpl_image_compare
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


@pytest.mark.mpl_image_compare
def test_visualize_disk_space_vertical(visualizer: Visualizer) -> plt.Figure:
    return visualizer.visualize_disk_space_vertical(
        pd.DataFrame(
            index=pd.Index(
                [
                    "0-200 GB",
                    "201-400 GB",
                    "401-600 GB",
                    "601-900 GB",
                    "901-1500 GB",
                    "1501-2000 GB",
                    "2001-3000 GB",
                    "3001-5000 GB",
                    "5001-9000 GB",
                    "9001-114256 GB",
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
    )
