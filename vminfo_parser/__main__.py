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
    """Get unsupported os counts from analyzer and pass the repsonse to outputs.

    Args:
        analyzer (Analyzer): Analyzer instance
        cli_output (CLIOutput): CLI Output instance
        visualizer (Visualizer | None): Visualizer instance, or None if no graph output desired
    """

    unsupported_counts = analyzer.get_unsupported_os_counts()
    cli_output.format_series_output(unsupported_counts)
    if visualizer is not None:
        visualizer.visualize_unsupported_os_distribution(unsupported_counts)


def get_supported_os(config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: Visualizer | None) -> None:
    """Get supported os counts from analyzer and pass the response to outputs

    Args:
        config (Config): Config instance
        analyzer (Analyzer): Analyzer instance
        cli_output (CLIOutput): CLI Output instance
        visualizer (Visualizer | None): Visualizer instance, or None if no graph output desired
    """

    supported_counts: pd.Series = analyzer.get_supported_os_counts()

    cli_output.format_series_output(supported_counts)
    if visualizer is not None:
        visualizer.visualize_supported_os_distribution(supported_counts, environment_filter=config.environment_filter)


def output_os_by_version(analyzer: Analyzer, cli_output: CLIOutput, visualizer: Visualizer | None) -> None:
    """Get os versions from analyzer and pass the result to outputs, once for each os.

    Args:
        analyzer (Analyzer): Analyzer instance
        cli_output (CLIOutput): CLI Output instance
        visualizer (Visualizer | None): Visualizer instance, or None if no graph output desired
    """

    def output_os_versions(os_name: str) -> None:
        """Get os versions from analyzer and pass the result to outputs.

        Args:
            os_name (str): OS name for this iteration
        """

        counts_dataframe = analyzer.get_os_version_distribution(os_name)
        cli_output.format_dataframe_output(counts_dataframe, os_name=os_name)
        if visualizer is not None:
            visualizer.visualize_os_version_distribution(counts_dataframe, os_name=os_name)

    analyzer.by_os(output_os_versions)


def get_disk_space_ranges(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: Visualizer | None
) -> None:
    """Get disk space ranges from analyzer and pass to outputs.

    Args:
        config (Config): Config instance
        analyzer (Analyzer): Analyzer instance
        cli_output (CLIOutput): CLI Output instance
        visualizer (Visualizer | None): Visualizer instance, or None if no graph output desired
    """

    disk_space_df = analyzer.get_disk_space(os_filter=config.os_name)
    if not disk_space_df.empty:
        cli_output.print_formatted_disk_space(disk_space_df, os_filter=config.os_name)
        if visualizer:
            if config.environment_filter == "all":
                visualizer.visualize_disk_space_horizontal(disk_space_df)
            else:
                visualizer.visualize_disk_space_vertical(disk_space_df, os_filter=config.os_name)


def get_os_counts(config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: Visualizer | None) -> None:
    """Get OS counts from analyzer and pass to outputs.

    Args:
        config (Config): Config instance
        analyzer (Analyzer): Analyzer instance
        cli_output (CLIOutput): CLI Output instance
        visualizer (Visualizer | None): Visualizer instance, or None if no graph output desired
    """

    counts: pd.Series = analyzer.get_operating_system_counts()
    cli_output.format_series_output(counts)

    if visualizer:
        visualizer.visualize_os_distribution(counts, config.count_filter)


def show_disk_space_by_os(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: Visualizer | None
) -> None:
    """Get disk space ranges from analyzer and pass to outputs, once for each os.

    Args:
        config (Config): Config instance
        analyzer (Analyzer): Analyzer instance
        cli_output (CLIOutput): CLI Output instance
        visualizer (Visualizer | None): Visualizer instance, or None if no graph output desired
    """

    def show_disk_space(os_name: str) -> None:
        """Get disk space ranges from analyzer and pass to outputs.

        Args:
            os_name (str):  OS name for this iteration
        """

        disk_space_df = analyzer.get_disk_space(os_filter=os_name)
        if not disk_space_df.empty:
            cli_output.print_formatted_disk_space(disk_space_df, os_filter=os_name)
            if visualizer:
                if config.environment_filter == "all":
                    visualizer.visualize_disk_space_horizontal(disk_space_df)
                else:
                    visualizer.visualize_disk_space_vertical(disk_space_df, os_filter=os_name)

    analyzer.by_os(show_disk_space)


def sort_by_site(vm_data: VMData, cli_output: CLIOutput) -> None:
    """Get resource usage by site and output using cli only.

    Args:
        vm_data (VMData): VMData instance
        cli_output (CLIOutput): CLI Output instance
    """
    site_dataframe = vm_data.create_site_specific_dataframe()
    cli_output.print_site_usage(["Memory", "CPU", "Disk", "VM"], site_dataframe)


def main(*args: str) -> None:  # noqa: C901
    config = Config.from_args(*args)
    if config.generate_yaml:
        config.generate_yaml_from_parser()
        exit()
    if config.directory:
        vm_data = VMData.from_file(config.directory)
    else:
        vm_data = VMData.from_file(config.file)

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

        case config.get_disk_space_ranges | config.over_under_tb | config.breakdown_by_terabyte:
            get_disk_space_ranges(config, analyzer, cli_output, visualizer)

        case config.get_os_counts:
            get_os_counts(config, analyzer, cli_output, visualizer)

        case config.output_os_by_version:
            output_os_by_version(analyzer, cli_output, visualizer)

        case config.get_supported_os:
            get_supported_os(config, analyzer, cli_output, visualizer)

        case config.get_unsupported_os:
            get_unsupported_os(analyzer, cli_output, visualizer)

    # Save results if necessary
    vm_data.save_to_csv("output.csv")

    # close clioutput
    cli_output.close()


if __name__ == "__main__":
    main()
