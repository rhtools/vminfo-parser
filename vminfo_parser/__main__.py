#!/usr/bin/env python3
# Std lib imports
import logging

# 3rd party imports
import pandas as pd

from .analyzer import Analyzer
from .clioutput import CLIOutput
from .config import Config
from .visualizer import Visualizer
from .vmdata import VMData

LOGGER = logging.getLogger(__name__)


def get_unsupported_os(analyzer: Analyzer, cli_output: CLIOutput, visualizer: Visualizer | None) -> None:
    unsupported_counts = analyzer.generate_unsupported_os_counts()
    cli_output.format_series_output(unsupported_counts)
    if visualizer is not None:
        visualizer.visualize_unsupported_os_distribution(unsupported_counts)


def get_supported_os(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: t.Optional[Visualizer]
) -> None:
    supported_counts: pd.Series = analyzer.get_supported_os_counts()

    cli_output.format_series_output(supported_counts)
    if visualizer is not None:
        visualizer.visualize_supported_os_distribution(supported_counts, environment_filter=config.environment_filter)


def output_os_by_version(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: Visualizer | None
) -> None:
    for os_name in analyzer.vm_data.df["OS Name"].unique():
        if os_name is not None and not pd.isna(os_name) and os_name != "":
            counts_dataframe = analyzer.generate_os_version_distribution(
                analyzer.vm_data.df, os_name, config.minimum_count
            )
            cli_output.format_dataframe_output(counts_dataframe, os_name=os_name)
            if visualizer is not None:
                visualizer.visualize_os_version_distribution(counts_dataframe, os_name)


def get_os_counts(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: t.Optional[Visualizer]
) -> None:
    counts: pd.Series = analyzer.get_operating_system_counts()
    cli_output.format_series_output(counts)

    if visualizer:
        visualizer.visualize_os_distribution(counts, config.minimum_count)


def get_disk_space_ranges(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: t.Optional[Visualizer]
) -> None:
    disk_space_df = analyzer.get_disk_space(os_filter=config.os_name)
    if not disk_space_df.empty:
        cli_output.print_formatted_disk_space(disk_space_df, os_filter=config.os_name)
        if visualizer:
            if config.environment_filter == "all":
                visualizer.visualize_disk_space_horizontal(disk_space_df)
            else:
                visualizer.visualize_disk_space_vertical(disk_space_df, os_filter=config.os_name)


def show_disk_space_by_os(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: t.Optional[Visualizer]
) -> None:
    os_names: list[str]
    if config.os_name:
        os_names = [config.os_name]
    else:
        os_names = analyzer.get_unique_os_names()

    for os_name in os_names:
        disk_space_df = analyzer.get_disk_space(os_filter=os_name)
        if not disk_space_df.empty:
            cli_output.print_formatted_disk_space(disk_space_df, os_filter=os_name)
            if visualizer:
                if config.environment_filter == "all":
                    visualizer.visualize_disk_space_horizontal(disk_space_df)
                else:
                    visualizer.visualize_disk_space_vertical(disk_space_df, os_filter=os_name)


def sort_by_site(vm_data: VMData, cli_output: CLIOutput) -> None:
    site_dataframe = vm_data.create_site_specific_dataframe()
    cli_output.print_site_usage(["Memory", "CPU", "Disk", "VM"], site_dataframe)


def main(*args: str) -> None:  # noqa: C901
    config = Config.from_args(*args)
    if config.generate_yaml:
        config.generate_yaml_from_parser()
        exit()
    vm_data = VMData.from_file(config.file)
    vm_data.set_column_headings()
    vm_data.add_extra_columns()

    visualizer: Visualizer | None = None
    if config.generate_graphs:
        visualizer = Visualizer()
    cli_output = CLIOutput()
    analyzer = Analyzer(vm_data, config)

    match True:
        case config.sort_by_site:
            sort_by_site(vm_data, cli_output)

        case config.show_disk_space_by_os:
            show_disk_space_by_os(config, analyzer, cli_output, visualizer)

        case config.get_disk_space_ranges:
            get_disk_space_ranges(config, analyzer, cli_output, visualizer)

        case config.get_os_counts:
            get_os_counts(config, analyzer, cli_output, visualizer)

        case config.output_os_by_version:
            output_os_by_version(config, analyzer, cli_output, visualizer)

        case config.get_supported_os:
            get_supported_os(config, analyzer, cli_output, visualizer)

        case config.get_unsupported_os:
            get_unsupported_os(analyzer, cli_output, visualizer)

    # Save results if necessary
    vm_data.save_to_csv("output.csv")

    # close clioutput
    analyzer.cli_output.close()
    cli_output.close()


if __name__ == "__main__":
    main()
