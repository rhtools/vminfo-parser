#!/usr/bin/env python3
# Std lib imports
import logging
import typing as t

# 3rd party imports
import pandas as pd

from .analyzer import Analyzer
from .clioutput import CLIOutput
from .config import Config
from .visualizer import Visualizer
from .vmdata import VMData

LOGGER = logging.getLogger(__name__)


def get_unsupported_os(analyzer: Analyzer, cli_output: CLIOutput, visualizer: t.Optional[Visualizer]) -> None:
    unsupported_counts = analyzer.generate_unsupported_os_counts()
    cli_output.format_series_output(unsupported_counts)
    if visualizer is not None:
        visualizer.visualize_unsupported_os_distribution(unsupported_counts)


def get_supported_os(
    config: Config, analyzer: Analyzer, cli_output: CLIOutput, visualizer: t.Optional[Visualizer]
) -> None:
    supported_counts: pd.Series
    if config.prod_env_labels and config.sort_by_env:
        supported_counts = analyzer.generate_supported_os_counts(
            *config.prod_env_labels.split(","),
            environment_filter=config.sort_by_env,
        )
    else:
        supported_counts = analyzer.generate_supported_os_counts(environment_filter=config.sort_by_env)

    cli_output.format_series_output(supported_counts)
    if visualizer is not None:
        visualizer.visualize_supported_os_distribution(supported_counts, environment_filter=config.sort_by_env)


def output_os_by_version(analyzer: Analyzer, cli_output: CLIOutput, visualizer: t.Optional[Visualizer]) -> None:
    for os_name, counts_dataframe in analyzer.generate_os_version_distribution():
        cli_output.format_dataframe_output(counts_dataframe, os_name=os_name)
        if visualizer is not None:
            visualizer.visualize_os_version_distribution(counts_dataframe, os_name)


def get_os_counts(config: Config, analyzer: Analyzer) -> None:
    if config.environments:
        if config.os_name:
            analyzer.sort_attribute_by_environment(
                *config.environments,
                attribute="operatingSystem",
                os_filter=config.os_name,
            )
        elif config.sort_by_env:
            analyzer.sort_attribute_by_environment(
                *config.environments,
                attribute="operatingSystem",
                environment_filter=config.sort_by_env,
            )
        else:
            analyzer.sort_attribute_by_environment(*config.environments, attribute="operatingSystem")
    else:
        if config.os_name:
            analyzer.sort_attribute_by_environment(attribute="operatingSystem", os_filter=config.os_name)
        else:
            analyzer.sort_attribute_by_environment(attribute="operatingSystem")


def get_disk_space_ranges(config: Config, analyzer: Analyzer) -> None:
    if config.sort_by_env != "all":
        analyzer.sort_attribute_by_environment(
            *config.environments,
            attribute="diskSpace",
            environment_filter=config.sort_by_env,
            over_under_tb=config.over_under_tb,
            show_disk_in_tb=config.breakdown_by_terabyte,
        )
    else:
        analyzer.sort_attribute_by_environment(
            attribute="diskSpace",
            environment_filter=config.sort_by_env,
            over_under_tb=config.over_under_tb,
            show_disk_in_tb=config.breakdown_by_terabyte,
        )


def show_disk_space_by_os(config: Config, vm_data: VMData, analyzer: Analyzer) -> None:
    if config.os_name:
        # If the user specifies an OS, use that to filter out everything else
        if config.environments:
            analyzer.sort_attribute_by_environment(
                *config.environments,
                attribute="diskSpace",
                os_filter=config.os_name,
                environment_filter=config.sort_by_env,
                over_under_tb=config.over_under_tb,
                show_disk_in_tb=config.breakdown_by_terabyte,
            )
        else:
            analyzer.plot_disk_space_distribution(
                os_name=config.os_name,
                show_disk_in_tb=config.breakdown_by_terabyte,
            )
    else:
        # If the user has not specified an OS name, assume they want them all
        for os_name in vm_data.df["OS Name"].unique():
            if config.environments:
                analyzer.sort_attribute_by_environment(
                    *config.environments,
                    attribute="diskSpace",
                    os_filter=os_name,
                    environment_filter=config.sort_by_env,
                    over_under_tb=config.over_under_tb,
                    granular_disk_space_by_os=config.disk_space_by_granular_os,
                )

            else:
                if config.over_under_tb:
                    analyzer.sort_attribute_by_environment(
                        os_name=os_name,
                        show_disk_in_tb=config.breakdown_by_terabyte,
                    )
                else:
                    analyzer.sort_attribute_by_environment(os_name=os_name)


def sort_by_site(vm_data: VMData, cli_output: CLIOutput) -> None:
    site_dataframe = vm_data.create_site_specific_dataframe()
    cli_output.print_site_usage(["Memory", "CPU", "Disk", "VM"], site_dataframe)


def main(*args: t.Optional[str]) -> None:  # noqa: C901
    config = Config.from_args(*args)
    if config.generate_yaml:
        config.generate_yaml_from_parser()
        exit()
    vm_data = VMData.from_file(config.file)
    vm_data.set_column_headings()
    vm_data.add_extra_columns()

    visualizer: Visualizer = None
    if config.generate_graphs:
        visualizer = Visualizer()
    cli_output = CLIOutput()
    analyzer = Analyzer(vm_data, config, column_headers=vm_data.column_headers)

    match True:
        case config.sort_by_site:
            sort_by_site(vm_data, cli_output)

        case config.show_disk_space_by_os:
            show_disk_space_by_os(config, vm_data, analyzer)

        case config.get_disk_space_ranges:
            get_disk_space_ranges(config, analyzer)

        case config.get_os_counts:
            get_os_counts(config, analyzer)

        case config.output_os_by_version:
            output_os_by_version(analyzer, cli_output, visualizer)

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
