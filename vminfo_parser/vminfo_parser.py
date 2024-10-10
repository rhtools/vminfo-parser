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


def main(*args: t.Optional[str]) -> None:  # noqa: C901
    config = Config()
    config = Config.from_args(*args)

    vm_data = VMData.from_file(config.file)
    vm_data.set_column_headings()
    vm_data.add_extra_columns()

    visualizer = Visualizer()
    cli_output = CLIOutput()
    analyzer = Analyzer(vm_data, config, column_headers=vm_data.column_headers)

    # Load environments from prod-env-labels if provided
    environments = []
    if config.prod_env_labels:
        environments = config.prod_env_labels.split(",")

    if config.sort_by_site:
        site_dataframe = vm_data.create_site_specific_dataframe()
        analyzer.cli_output.print_site_usage(["Memory", "CPU", "Disk", "VM"], site_dataframe)

    # Check if environments are defined for sorting
    if config.sort_by_env and not environments:
        LOGGER.critical(
            "You specified you wanted to sort by environment but "
            "did not provide a definition of what categorizes a Prod environment... exiting"
        )
        exit()

    if config.generate_yaml:
        config.generate_yaml_from_parser()
    if config.show_disk_space_by_os:
        if config.os_name:
            # If the user specifies an OS, use that to filter out everything else
            if environments:
                analyzer.sort_attribute_by_environment(
                    *environments,
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
                if environments:
                    analyzer.sort_attribute_by_environment(
                        *environments,
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

    if config.get_disk_space_ranges:
        if config.sort_by_env != "all":
            if environments:
                analyzer.sort_attribute_by_environment(
                    *environments,
                    attribute="diskSpace",
                    environment_filter=config.sort_by_env,
                    over_under_tb=config.over_under_tb,
                    show_disk_in_tb=config.breakdown_by_terabyte,
                )
            else:
                LOGGER.critical(
                    """Failed to determine prod from non-prod environments...
                    Perhaps you did not pass in the --prod-env-labels ?"""
                )
                exit()
        else:
            analyzer.sort_attribute_by_environment(
                attribute="diskSpace",
                environment_filter=config.sort_by_env,
                over_under_tb=config.over_under_tb,
                show_disk_in_tb=config.breakdown_by_terabyte,
            )

    if config.get_os_counts:
        if environments:
            if config.os_name:
                analyzer.sort_attribute_by_environment(
                    *environments,
                    attribute="operatingSystem",
                    os_filter=config.os_name,
                )
            elif config.sort_by_env:
                analyzer.sort_attribute_by_environment(
                    *environments,
                    attribute="operatingSystem",
                    environment_filter=config.sort_by_env,
                )
            else:
                analyzer.sort_attribute_by_environment(*environments, attribute="operatingSystem")
        else:
            if config.os_name:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem", os_filter=config.os_name)
            else:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem")

    if config.output_os_by_version:
        for os_name in vm_data.df["OS Name"].unique():
            if os_name is not None and not pd.isna(os_name) and os_name != "":
                counts_dataframe = analyzer.generate_os_version_distribution(vm_data.df, os_name, config.minimum_count)
                cli_output.format_dataframe_output(counts_dataframe, os_name=os_name)
                if config.generate_graphs:
                    visualizer.visualize_os_version_distribution(counts_dataframe, os_name)

    if config.get_supported_os:
        supported_counts: pd.Series
        if config.prod_env_labels and config.sort_by_env:
            supported_counts = analyzer.generate_supported_os_counts(
                *config.prod_env_labels.split(","),
                environment_filter=config.sort_by_env,
            )
        else:
            supported_counts = analyzer.generate_supported_os_counts(environment_filter=config.sort_by_env)

        cli_output.format_series_output(supported_counts)
        if config.generate_graphs:
            visualizer.visualize_supported_os_distribution(supported_counts, environment_filter=config.sort_by_env)

    if config.get_unsupported_os:
        unsupported_counts = analyzer.generate_unsupported_os_counts()
        cli_output.format_series_output(unsupported_counts)
        if config.generate_graphs:
            visualizer.visualize_unsupported_os_distribution(unsupported_counts)

    # Save results if necessary
    vm_data.save_to_csv("output.csv")

    # close clioutput
    analyzer.cli_output.close()
    cli_output.close()


if __name__ == "__main__":
    main()
