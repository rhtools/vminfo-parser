#!/usr/bin/env python3

import pandas as pd
import matplotlib
# Set non-interactive mode by default
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as ticker
import numpy as np
from fuzzywuzzy import process
import magic
import argparse


# This program expects a CSV with the following headings
# VM Power,	VM OS,	VM CPU,	VM MEM (GB), VM Provisioned (GB), VM Used (GB),	Environment	
# The add_extra_columns will add OS Name, OS Version and Architecture
# sample data:
#|VM Power	|VM OS		        |VM CPU |VM MEM (GB)|VM Provisioned (GB)|VM Used (GB)|Environment	
#|PoweredOn	|CentOS 4/5 (32-bit)|	2   |	2	    | 82.112 	        |25.831	     |Test
# While it is likely that this format is not standard to your environment, this program should be able to be
# altered slightly to match what your requirements are

# The primary purpose of this script is to aide in the assessment of migration to OpenShift Virtualization


def format_dataframe_output(dataFrame):
    if dataFrame.index.nlevels == 2:
        pass
    else:
        os_version = dataFrame.reset_index()['index'].values
        count = dataFrame.reset_index()['OS Version'].values

        print("")
        print(os_name)
        print('--------------')
        print("OS Version\t\t\t Count")
        for version, count_value in zip(os_version, count):
            print(f"{version.ljust(32)} {count_value}")


def get_file_type(file_path):
    """
    Returns the MIME type of the file located at the specified file path.

    Args:
        file_path (str): The path to the file for which the MIME type should be determined.

    Returns:
        str: The MIME type of the file.

    Raises:
        FileNotFoundError: If the file at the specified file path does not exist.
    """
    mime_type = magic.from_file(file_path, mime=True)
    return mime_type

def find_fuzzy_match_in_dataframe(df, text):
    """
    Finds a fuzzy match for the given text in the column headings of a DataFrame.

    Args:
        df: pandas DataFrame. The DataFrame to search for fuzzy matches.
        text: str. The text to find a fuzzy match for in the column headings.

    Returns:
        str or None. The name of the column that matched the text fuzzily, or None if no match was found.
    """
    for column in df.columns:
        _, score = process.extractOne(text, [column])
        
        if score >= 80:  # Adjust the threshold as needed
            return column
    
    return None

def add_extra_columns(dataFrame):
    """
    Adds extra columns to the DataFrame by extracting OS name, version, and architecture information from the 'VM OS' column using a regex pattern.

    Args:
        dataFrame: DataFrame containing VM OS information.

    Returns:
        None
    """
    # Only attempt to add columns if the 3 columns don't already exist
    if not all(col in dataFrame.columns for col in ['OS Name', 'OS Version', 'Architecture']):
        # Define a regex pattern to extract OS name, version, and architecture information
        pattern = r"^(?P<OS_Name>.*?)\s*(?P<OS_Version>(?:\d+\s+\w+|\w+)\s*(?:or later)?\s*)?\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\)"
        
        # Extract the matched groups using str.extract and assign them to new columns in the DataFrame
        dataFrame[['OS Name', 'OS Version', 'Architecture']] = dataFrame['VM OS'].str.extract(pattern)
        
        # Fill NaN values in the newly created columns with the original 'VM OS' column values
        dataFrame['OS Name'].fillna(dataFrame['VM OS'], inplace=True)
        dataFrame['OS Version'].fillna(dataFrame['VM OS'], inplace=True)
        dataFrame['Architecture'].fillna(dataFrame['VM OS'], inplace=True)
        
        # Save the modified DataFrame to a CSV file
        dataFrame.to_csv('/tmp/Inventory_VMs_redhat_06_27_24.csv', index=False)
    else:
        print("All columns already exist")

def generate_supported_OS_counts(dataFrame):
    """
    Generates a horizontal bar chart displaying the distribution of supported operating systems based on their frequency in the DataFrame.

    Args:
        dataFrame: DataFrame containing OS information.

    Returns:
        None
    """

    # Calculate the frequency of each unique OS name
    counts = dataFrame['OS Name'].value_counts()

    # Define specific colors for identified OS names
    supported_os_colors = {
        'Red Hat Enterprise Linux': 'red',
        'SUSE Linux Enterprise': 'green',
        'Microsoft Windows Server': 'navy',
        'Microsoft Windows': 'blue'
        # Add more OS names and colors as needed
    }

    # Filter counts based on keys in supported_os_colors
    filtered_counts = counts[counts.index.isin(supported_os_colors.keys())]

    # Generate colors for filtered OS names based on supported_os_colors
    colors = [supported_os_colors[os] for os in filtered_counts.index]

    # Plot the supported OS counts as a horizontal bar chart with specified colors
    filtered_counts.plot(kind='barh', rot=45, color=colors)
    if args.generate_graphs:
        # Set titles and labels for the plot
        plt.title('Supported Operating System Distribution')
        plt.ylabel('Operating Systems')
        plt.xlabel('Count')
        plt.xscale('log')
        plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.xticks([filtered_counts.iloc[0] - (filtered_counts.iloc[0] % 100), filtered_counts.iloc[len(filtered_counts)//2] - (filtered_counts.iloc[len(filtered_counts)//2] % 100), filtered_counts.iloc[-1]])

        # Save and display the plot
        plt.show(block=True)
        plt.close()

def generate_unsupported_OS_counts(dataFrame):
    """
    Generates a pie chart displaying the distribution of unsupported operating systems based on their frequency in the DataFrame.

    Args:
        dataFrame: DataFrame containing OS information.

    Returns:
        None
    """

    # Calculate the frequency of each unique OS name
    counts = dataFrame['OS Name'].value_counts()

    # Define specific colors for identified supported OS names
    supported_os = ['Red Hat Enterprise Linux', 'SUSE Linux Enterprise', 'Microsoft Windows Server', 'Microsoft Windows']

    # Filter out supported OS counts
    unsupported_counts = counts[~counts.index.isin(supported_os)]
    
    # Combine unsupported OS under 0.7% into "Other" category
    threshold = 0.0075
    other_counts = unsupported_counts[unsupported_counts / unsupported_counts.sum() < threshold]
    other_total = other_counts.sum()
    unsupported_counts = unsupported_counts[~unsupported_counts.index.isin(other_counts.index)]
    unsupported_counts['Other'] = other_total
    print(unsupported_counts)
    # Create a pie chart for unsupported OS distribution
    random_colors = cm.rainbow(np.linspace(0, 1, len(unsupported_counts)))
    if args.generate_graphs:
        plt.pie(unsupported_counts, labels=unsupported_counts.index, colors=random_colors, autopct='%1.1f%%')
        plt.title('Unsupported Operating System Distribution')

        # Save and display the plot
        plt.show(block=True)
        plt.close()

def generate_all_OS_counts(dataFrame, minimumCount=500, maximumCount=99999):
    """
    Generates a horizontal bar chart displaying the distribution of operating systems based on their frequency in the DataFrame.

    Args:
        dataFrame: DataFrame containing OS information.
        minimumCount: The minimum number of VMs within a certain OS category to display. Default: 500
        maximumCount: The maximum number of VMs within a certain OS category to display. Largely symbolic. Default 99999

    Returns:
        None
    """
    # Calculate the frequency of each unique OS name
    counts = dataFrame['OS Name'].value_counts()

    # Filter counts within the set thresholds
    filtered_counts = counts[(counts >= minimumCount) & (counts <= maximumCount)]

    # Define specific colors for identified OS names
    os_colors = {
        'Red Hat Enterprise Linux': 'red',
        'SUSE Linux Enterprise': 'green',
        'Microsoft Windows Server': 'navy',
        'Microsoft Windows': 'blue',
        "Ubuntu": "orange",
        "Oracle Linux": "maroon",
        "unknown": "grey"
        # Add more OS names and colors as needed
    }

    # Generate random colors for bars not in supported_os_colors
    random_colors = cm.rainbow(np.linspace(0, 1, len(filtered_counts)))
    colors = [os_colors.get(os, random_colors[i]) for i, os in enumerate(filtered_counts.index)]

    # Plot the filtered counts as a horizontal bar chart with specified and random colors
    filtered_counts.plot(kind='barh', rot=45, color=colors)
    print(filtered_counts)
    if args.generate_graphs:

        # Set titles and labels for the plot
        plt.title('Operating System Distribution')
        plt.ylabel('Operating Systems')
        plt.xlabel('Count')
        plt.xscale('log')
        plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
        plt.xticks([filtered_counts.iloc[0] - (filtered_counts.iloc[0] % 100), filtered_counts.iloc[len(filtered_counts)//2] - (filtered_counts.iloc[len(filtered_counts)//2] % 100), filtered_counts.iloc[-1]])

        # Save and display the plot
        plt.show(block=True)
        plt.close()

def os_by_version(dataFrame, os_name):
    """
    Filters the DataFrame by the specified OS name and plots the distribution of OS versions for the filtered data.

    Args:
        dataFrame: DataFrame containing OS information.
        os_name: Name of the operating system to filter by.

    Returns:
        None
    """

    # Filter rows where the OS name matches the input parameter
    filtered_df = dataFrame[(dataFrame['OS Name'] == os_name)]
    # Calculate the frequency of each unique OS version
    #counts = filtered_df['OS Version'].value_counts()
    counts = filtered_df['OS Version'].fillna('unknown').value_counts()
    # We want to print out a text table and not the dataframe

    format_dataframe_output(counts)
    # Plot the counts as a horizontal bar chart
    counts.plot(kind='barh', rot=45)
    if args.generate_graphs:
        # Print the filtered DataFrame    
        # Set titles and labels for the plot
        plt.title(f'Distribution of {os_name}')
        plt.ylabel('OS Version')
        plt.xlabel('Count')
        plt.show(block=True)
        plt.close()


def calculate_disk_space_ranges(dataFrame, greater_than_2000=False, frameHeading="VM Provisioned (GB)"):
    """
    Calculates disk space ranges based on the provisioned disk space of virtual machines in the DataFrame.

    Args:
        dataFrame: DataFrame containing disk space information for virtual machines.
        greater_than_2000: Boolean flag to determine the disk space ranges (default: False).

    Returns:
        List of disk space ranges with VMs falling within each range.
    """

    # Determine the minimum and maximum disk space provisioned across all VMs
    min_disk_space = int(dataFrame[frameHeading].min())
    max_disk_space = int(dataFrame[frameHeading].max())
    
    # Define the final range based on the maximum disk space provisioned
    if max_disk_space > 9000:
        final_range = (9001, max_disk_space)
    else:
        final_range = (10001, 15000)
    
    if greater_than_2000:
        disk_space_ranges = [
        (min_disk_space, 2000),  
        (2001, 9000), 
        final_range
    ]
    else:
        # Define predefined disk space ranges
        disk_space_ranges = [
            (min_disk_space, 200), 
            (201, 400), 
            (401, 600), 
            (601, 900), 
            (901, 1500), 
            (1501, 2000), 
            (2001, 3000), 
            (3001, 5000),
            (5001, 9000), 
            final_range
        ]
        
    # Identify which VMs fall within each defined range
    disk_space_ranges_with_vms = []
    for range_start, range_end in disk_space_ranges:
        vms_in_range = dataFrame[(dataFrame[frameHeading] >= range_start) & (dataFrame[frameHeading] <= range_end)]
        if not vms_in_range.empty:
            disk_space_ranges_with_vms.append((range_start, range_end))
    
    return disk_space_ranges_with_vms


def plot_disk_space_distribution(dataFrame, os_name=None, os_version=None, greater_than_2000=False, frameHeading="VM Provisioned (GB)"):
    """
    Plots the distribution of disk space for virtual machines based on specified criteria.

    Args:
        dataFrame: DataFrame containing disk space information for virtual machines.
        os_name: Name of the operating system (default: None).
        os_version: Version of the operating system (default: None).
        greater_than_2000: Boolean flag to filter disk space greater than 2000 GB (default: False).

    Returns:
        None
    """

    # Create a subplot for plotting
    fig, ax = plt.subplots()
    
    # Calculate disk space ranges and update the DataFrame with the corresponding disk space range for each VM
    disk_space_ranges = calculate_disk_space_ranges(dataFrame, greater_than_2000=greater_than_2000, frameHeading=frameHeading)
    
    # Filter machines based on disk space condition
    
    
    # Assign disk space ranges to a new column in the DataFrame
    for lower, upper in disk_space_ranges:
        mask = (dataFrame['VM Provisioned (GB)'] >= lower) & (dataFrame['VM Provisioned (GB)'] <= upper)
        dataFrame.loc[mask, 'Disk Space Range'] = f'{lower}-{upper} GB'
    
    # Count the number of VMs in each disk space range
    range_counts = {range_: 0 for range_ in disk_space_ranges}
    for lower, upper in disk_space_ranges:
        mask = (dataFrame['VM Provisioned (GB)'] >= lower) & (dataFrame['VM Provisioned (GB)'] <= upper)
        count = dataFrame.loc[mask].shape[0]
        range_counts[(lower, upper)] = count
    
    # Sort the counts and plot them as a horizontal bar chart
    sorted_dict = dict(sorted(range_counts.items(), key=lambda x: x[1]))
    print("Disk Space Range (GB)\t\tCount")
    for disk_range in range_counts.items():
        # The first indexed item is a tuple that represents the disk space range
        # so we need to take the first and the second number and convert it to a str
        # for better printing
        disk_range_str =f"{disk_range[0][0]}-{disk_range[0][1]}"
        print(f"{disk_range_str.ljust(32)} {disk_range[1]}")
    if args.generate_graphs:
        for range_, count in sorted_dict.items():
            if os_name:
                ax.barh(f'{range_[0]}-{range_[1]} GB', count, label=os_name)
            else:
                ax.barh(f'{range_[0]}-{range_[1]} GB', count)
        
        # Set titles and labels for the plot
        ax.set_ylabel('Disk Space Range')
        ax.set_xlabel('Number of Machines')
        #ax.set_xscale('log')
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        
        if os_name and os_version:
            ax.set_title(f'Hard Drive Space Breakdown for {os_name} {os_version}')
        elif os_name:
            ax.set_title(f'Hard Drive Space Breakdown for {os_name}')
        else:
            ax.set_title('Hard Drive Space Breakdown for All Environments')
        ax.set_xlim(right=max(range_counts.values()) + 1.5)

        # Display the plot
        plt.show(block=True)
        plt.close()


def disk_use_by_attribute(dataFrame, os_name, os_version=None, frameHeading="VM Provisioned (GB)"):
    """
    Filters the DataFrame by the specified OS name and version (if provided) and plots disk space distribution for the filtered data.

    Args:
        dataFrame: DataFrame containing disk space information.
        os_name: Name of the operating system to filter by.
        os_version: Version of the operating system to further filter by (default: None).

    Returns:
        None
    """

    # Filter the DataFrame by OS name, and further by OS version if specified
    filtered_df = dataFrame[dataFrame['OS Name'] == os_name]
    if os_version:
        filtered_df = filtered_df[filtered_df['OS Version'] == os_version]
    
    # Call the function to plot disk space distribution for the filtered DataFrame
    plot_disk_space_distribution(filtered_df, os_name, os_version, frameHeading=frameHeading)


def disk_use_for_environment(dataFrame, filter_diskspace=False, frameHeading="VM Provisioned (GB)"):
    """
    Calculates and plots disk space distribution for the given DataFrame.

    Args:
        dataFrame: DataFrame containing disk space information.
        filter_diskspace: Boolean flag to filter disk space greater than 1500 (defgenerate_all_OS_counts(df)
    # generate_supported_OS_counts(df)
    # generate_unsupported_OS_counts(df)
ault: False).

    Returns:
        None
    """

    # Call the function to plot disk space distribution for the entire DataFrame
    plot_disk_space_distribution(dataFrame, greater_than_2000=filter_diskspace, frameHeading=frameHeading)

def categorize_environment(x, *args):
    """
    Categorizes the environment based on the presence of specified keywords.

    Args:
        x: Input string to categorize.
        *args: Variable number of keywords to check for in the input string.

    Returns:
        Categorized environment as 'prod' if any of the specified keywords are present, otherwise 'non-prod'.
    """
    # if the user has not passed in any arguments denoting which things should be classified as prod
    # assume they want a count of OS' across all environments
    if not args:
        return 'all envs'
    for arg in args:
        if arg in x:
            return 'prod'
    return 'non-prod'


def sort_attribute_by_environment(dataFrame, *env_keywords, attribute="operatingSystem", os_filter=None, environment_filter=None):
    data_cp = dataFrame.copy()
    data_cp['Environment'] = dataFrame['Environment'].apply(categorize_environment, args=env_keywords)

    if os_filter:
        data_cp = data_cp[data_cp['OS Name'] == os_filter]

    if environment_filter and environment_filter not in ["all", "both"]:
        data_cp = data_cp[data_cp['Environment'] == environment_filter]

    if data_cp.empty:
        print(f"None found in {environment_filter} \n")
        return

    if attribute == "operatingSystem":
        handle_operating_system(data_cp, environment_filter)
    elif attribute == "diskSpace":
        handle_disk_space(data_cp, environment_filter, env_keywords, os_filter)

def handle_operating_system(data_cp, environment_filter):
    if not environment_filter:
        counts = data_cp['OS Name'].value_counts()
    else:
        counts = data_cp.groupby('Environment')['OS Name'].value_counts()

    filtered_counts = counts[counts >= 100]
    print(filtered_counts)

    os_names = [idx[1] for idx in filtered_counts.index] if filtered_counts.index.nlevels == 2 else filtered_counts.index
    os_colors = {
        'Red Hat Enterprise Linux': 'red',
        'SUSE Linux Enterprise': 'green',
        'Microsoft Windows Server': 'navy',
        'Microsoft Windows': 'blue',
        "Ubuntu": "orange",
        "Oracle Linux": "maroon",
        "unknown": "grey"
    }

    random_colors = cm.rainbow(np.linspace(0, 1, len(filtered_counts)))
    colors = [os_colors.get(os, random_colors[i]) for i, os in enumerate(os_names)]

    ax = filtered_counts.plot(kind='barh', rot=45, color=colors)
    ax.set_yticklabels([f"{os[1]} - {os[0]}" for os in filtered_counts.index])
    if args.generate_graphs:
        plt.xlabel('Count')
        plt.title('OS Counts by Environment Type (>= 100)')
        plt.show(block=True)

def handle_disk_space(data_cp, environment_filter, env_keywords, os_filter):
    disk_space_ranges = calculate_disk_space_ranges(data_cp)
    for lower, upper in disk_space_ranges:
        mask = (data_cp['VM Provisioned (GB)'] >= lower) & (data_cp['VM Provisioned (GB)'] <= upper)
        data_cp.loc[mask, 'Disk Space Range'] = f'{lower}-{upper} GB'

    if environment_filter is None:
        environment_filter = "all"

    if environment_filter == "both":
        range_counts_by_environment = data_cp.groupby(['Disk Space Range', 'Environment']).size().unstack(fill_value=0)
    elif environment_filter == "all":
        range_counts_by_environment = data_cp['Disk Space Range'].value_counts().reset_index()
        range_counts_by_environment.columns = ['Disk Space Range', 'Count']
        range_counts_by_environment.set_index('Disk Space Range', inplace=True)
    else:
        range_counts_by_environment = data_cp[data_cp['Environment'] == environment_filter].groupby(['Disk Space Range', 'Environment']).size().unstack(fill_value=0)

    range_counts_by_environment['second_number'] = range_counts_by_environment.index.str.split('-').str[1].str.split().str[0].astype(int)
    sorted_range_counts_by_environment = range_counts_by_environment.sort_values(by='second_number', ascending=True)
    sorted_range_counts_by_environment.drop('second_number', axis=1, inplace=True)

    if os_filter:
        print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords, os_filter=os_filter)
    else:
        print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords)    
    sorted_range_counts_by_environment.plot(kind='bar', stacked=False, figsize=(12, 8), rot=45)
    if args.generate_graphs:
        plt.xlabel('Disk Space Range')
        plt.ylabel('Number of VMs')
        plt.title(f'VM Disk Size Ranges Sorted by Environment {f"for {os_filter}" if os_filter else ""}')
        plt.show(block=True)

def print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords, os_filter=None):
    col_widths = {'Environment': 22, **{env: 10 for env in sorted_range_counts_by_environment.columns}} if env_keywords and environment_filter != "all" else {**{env: 17 for env in sorted_range_counts_by_environment.columns}}
    formatted_rows = []
    if environment_filter == "all":
        formatted_rows.append('Disk Space Range'.ljust(20) + 'Count'.ljust(col_widths['Count']))

    for index, row in sorted_range_counts_by_environment.iterrows():
        formatted_row = [str(index).ljust(15)]
        for col_name, width in col_widths.items():
            value = str(row[col_name]) if col_name in row.index else ""
            formatted_row.append(value.ljust(width))
        formatted_rows.append(' '.join(formatted_row))

    formatted_df_str = '\n'.join(formatted_rows)

    temp_heading = ''
    if os_filter:
        print(os_filter)
        print('---------------------------------')

    for headings in list(col_widths.keys()):
        if temp_heading:
            temp_heading += headings.ljust(11)
        else:
            temp_heading += headings.ljust(39)
    print(temp_heading)
    print(formatted_df_str)
    print()

def calculate_average_ram(df, environment_type):
    """
    Calculates the average RAM used for each OS that matches the specified environment type and prints the results in a formatted column layout.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        environment_type (str): The environment type to filter the data.

    Returns:
        None
    """

    # Get unique OS values from the DataFrame
    os_values = df['OS Name'].unique()

    # Print column headers for OS and Average RAM
    print("{:<20} {:<10}".format("OS", "Average RAM (GB)"))
    print("-" * 30)

    # Loop through each unique OS value
    for os in os_values:
        # Filter hosts based on OS and environment type
        filtered_hosts = df[(df['OS Name'] == os) & (df['Environment'].str.contains(environment_type))]
        
        # Calculate and print average RAM if hosts are found
        if not filtered_hosts.empty:
            avg_ram = filtered_hosts['VM MEM (GB)'].mean()
            print("{:<20} {:<10.2f}".format(os, avg_ram))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some arguments.')
    disk_group = parser.add_argument_group('Disk Space Analysis', 'Options related to generating disk ranges by os, environment or both')
    os_group = parser.add_argument_group('Operating System Analysis', 'Options related to generating OS type break downby OS version, environment or both')
    generic_group = parser.add_argument_group('Arguments that apply to both OS and Disk')
    generic_group.add_argument('--sort-by-env', type=str, nargs='?', help='Sort disk by environment. Use "all" to get combine count, "both" to show both non-prod and prod, or specify one.')
    generic_group.add_argument('--prod-env-labels', type=str, nargs='?', help="The values in your data that represent prod environments. This is used to generate prod and non-prod stats. Passed as CSV i.e. --prod-env-labels 'baker,dte'")
    generic_group.add_argument('--generate-graphs', action='store_true', help='Choose whether or not to output visual graphs. If this option is not set, a text table will be outputted to the terminal')
    disk_group.add_argument('--get-disk-space-ranges', action='store_true', help="This flag will get disk space ranges regardless of OS. Can be combine with --prod-env-labels and --sort-by-env to target a specific environment")
    disk_group.add_argument('--show-disk-space-by-os', action='store_true', help='Show disk space by OS')
    os_group.add_argument('--output-os-by-version', action='store_true', help='Output OS by version')
    os_group.add_argument('--get-os-counts', action='store_true', help='Generate a report that counts the inventory broken down by OS')
    os_group.add_argument('--os-name', type=str, help='The name of the Operating System to produce a report about')
    args = parser.parse_args()


    def required_if(argument, value):
        def required(argument_value):
            if argument_value == value and getattr(args, argument) is None:
                raise argparse.ArgumentTypeError(f'{argument} is required when using --sort-by-env')
            return argument_value
        return required
    args.sort_by_env = required_if('sort_by_env', '--sort-by-env')(args.sort_by_env)


    # Load the CSV file
    #df = pd.read_csv('/home/stratus/temp/Inventory_VMs_redhat_06_27_24_edited.csv')
    #file_path = "/home/stratus/Downloads/RVTools_tabvInfo.csv"
    #file_path = "/home/stratus/Downloads/SC_Datacenter_Output.csv"
    file_path = '/home/stratus/temp/Inventory_VMs_redhat_06_27_24_edited.csv'
    file_type = get_file_type(file_path)
    
   
    if args.generate_graphs:
        # If the user wants to see graphs, set the interactive mode on matplotlib
        matplotlib.use('TkAgg')

    # assuming someone has provided prod labels, we need to split them
    environments = []
    if args.prod_env_labels:
        environments = args.prod_env_labels.split(',')
    if args.sort_by_env and not environments:
        print("\n\nYou specified you wanted to sort by environment but did not provide a definition of what categorizes a Prod environment... exiting\n")
        exit()

    if "csv" in file_type:
        df = pd.read_csv(file_path)
    elif "spreadsheetml" in file_type:
        df = pd.read_excel(file_path)
    else:
        print("File passed in was neither a CSV nor an Excel file\nBailing...")
        exit()

    add_extra_columns(df)
    
   
    # Call the function for each unique OS name in the 'OS Name' dataframe
    unique_os_names = df['OS Name'].unique()

    ############## DISK RELATED OPTIONS
    ###
    if args.show_disk_space_by_os:
        # If the user specifies an OS,use that to filter out everything else
        if args.os_name:
            # If the user has defined what values indicuate a prod environment, sort between prod and non-prod
            if environments:
                if args.sort_by_env:
                    sort_attribute_by_environment(df, attribute="diskSpace", os_filter=args.os_name, environment_filter=args.sort_by_env, *environments)    
                else:
                    sort_attribute_by_environment(df, attribute="diskSpace", os_filter=args.os_name, *environments)
            else:
                sort_attribute_by_environment(df, attribute="diskSpace", os_filter=args.os_name)
        else:
            # If the user has not specified an OS name, assume they want them all
            for os_name in unique_os_names:
                if environments:           
                    sort_attribute_by_environment(df, attribute="diskSpace", os_filter=os_name,environment_filter=args.sort_by_env, *environments)
                    matplotlib.pyplot.close()
                else:
                    sort_attribute_by_environment(df, attribute="diskSpace", os_filter=os_name)
                    matplotlib.pyplot.close()

    if args.get_disk_space_ranges or args.show_disk_space_by_os:
        if args.sort_by_env == 'all':
            if args.show_disk_space_by_os:
                if environments and args.sort_by_env:
                    sort_attribute_by_environment(df, attribute="diskSpace",environment_filter=args.sort_by_env, *environments )
                else:
                    print("Missing information regarding how to sort the environment between prod and non-prod")
                    exit()
            else:
                sort_attribute_by_environment(df, attribute="diskSpace", environment_filter=args.sort_by_env)
                #disk_use_for_environment(df)
        elif args.sort_by_env:
            if args.get_disk_space_ranges and environments:
                sort_attribute_by_environment(df, environment_filter=args.sort_by_env,  attribute="diskSpace", *environments)
        else:
            disk_use_for_environment(df)

    ###
    ############# END DISK SECTION



    ############# OPERATING SYSTEM
    ###
    if args.output_os_by_version:
        for os_name in unique_os_names:
            os_by_version(df, os_name)

    if args.get_os_counts:
        if environments:
            if args.os_name:
                sort_attribute_by_environment(df, attribute="operatingSystem", os_filter=args.os_name, *environments)
            elif args.sort_by_env:
                sort_attribute_by_environment(df, attribute="operatingSystem", *environments, environment_filter=args.sort_by_env)
            else:
                sort_attribute_by_environment(df, attribute="operatingSystem", *environments)
        else:
            if args.os_name:
                sort_attribute_by_environment(df, attribute="operatingSystem", os_filter=args.os_name)
            else:
                sort_attribute_by_environment(df, attribute="operatingSystem")
    
    ###
    ############# END OPERATING SYSTEM SECTION


    #sort_attribute_by_environment(df, "test", attribute="diskSpace", os_filter="Red Hat Enterprise Linux", environment_filter="prod")

    #os_by_version(df, "Microsoft Windows")

    # disk_use_for_environment(df, filter_diskspace=True, frameHeading="VM Used (GB)")

    # disk_use_for_environment(df, filter_diskspace=False, frameHeading="VM Used (GB)")

    # generate_all_OS_counts(df)
    # generate_supported_OS_counts(df)
    # generate_unsupported_OS_counts(df)

