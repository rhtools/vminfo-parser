#!/usr/bin/env python3

import pandas as pd
import matplotlib
# Set non-interactive mode by default
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as ticker
import numpy as np
#from fuzzywuzzy import process
import magic
import argparse
import re

# This program expects a CSV with the following headings
# VM Power,	VM OS,	VM CPU,	VM MEM (GB), VM Provisioned (GB), VM Used (GB),	Environment	
# The add_extra_columns will add OS Name, OS Version and Architecture
# sample data:
#|VM Power	|VM OS		        |VM CPU |VM MEM (GB)|VM Provisioned (GB)|VM Used (GB)|Environment	
#|PoweredOn	|CentOS 4/5 (32-bit)|	2   |	2	    | 82.112 	        |25.831	     |Test
# While it is likely that this format is not standard to your environment, this program should be able to be
# altered slightly to match what your requirements are

# The primary purpose of this script is to aide in the assessment of migration to OpenShift Virtualization


def set_column_headings(dataFrame):
    global column_headers
        
    version1_columns = {"operatingSystem": "VM OS", "environment": "Environment", "vmMemory": 'VM MEM (GB)', "vmDisk": 'VM Provisioned (GB)'}
    version2_columns = {"operatingSystem": "OS according to the configuration file", "environment": "ent-env", "vmMemory": 'Memory', "vmDisk": 'Total disk capacity MiB'}
    if all(col in dataFrame.columns for col in version1_columns.values()):
        print("\nAll version 1 columns are present in the DataFrame.\n")
        column_headers = version1_columns
        column_headers["unitType"] = 'GB'
    elif all(col in dataFrame.columns for col in version2_columns.values()):
        print("\nAll version 2 columns are present in the DataFrame.\n")
        column_headers = version2_columns
        column_headers["unitType"] = 'MB'
    else:
        print(f"Missing column headers from either {version1_columns.values} or {version2_columns.values}")
        raise ValueError("Headers don't match either of the versions expected")

    # drop everything but the needed columns
    # Assuming column_headers is the global dictionary containing the column headers

    
    
def format_dataframe_output(dataFrame):
    """
    Format the output of a pandas DataFrame containing OS version and count data.

    Args:
        dataFrame (pandas.DataFrame): The DataFrame containing OS version and count data.

    Returns:
        None

    Examples:
        format_dataframe_output(dataFrame)
    """

    if dataFrame.index.nlevels == 2:
        pass
    else:
        os_version = dataFrame['OS Version'].values
        count = dataFrame['Count'].values
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
    os_column = column_headers['operatingSystem']
    windows_server_columns = ['Server OS Name', 'Server OS Version', 'Server Architecture']
    windows_desktop_columns = ['Desktop OS Name', 'Desktop OS Version', 'Desktop Architecture']
    if not all(col in dataFrame.columns for col in ['OS Name', 'OS Version', 'Architecture']):
        # Define a regex pattern to extract OS name, version, and architecture information
        exclude_windows_pattern = r"^(?!.*Microsoft)(?P<OS_Name>.*?)(?:\s+(?P<OS_Version>\d+(?:/\d+)*\s*(?:or later)?\s*)?\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\))"
        windows_server_pattern = r"^(?P<OS_Name>Microsoft Windows Server)\s+(?P<OS_Version>\d+(?:\.\d+)*(?:\s*R\d+)?(?:\s*SP\d+)?)(?:\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\))?"
        windows_desktop_pattern = r"^(?P<OS_Name>Microsoft Windows)\s+(?!Server)(?P<OS_Version>XP Professional|\d+(?:\.\d+)*|Vista|7|8|10)\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\)"

        # Extract the matched groups using str.extract and assign them to new columns in the DataFrame
        dataFrame[['OS Name', 'OS Version', 'Architecture']] = dataFrame[os_column].str.extract(exclude_windows_pattern)
        dataFrame[windows_server_columns] = dataFrame[os_column].str.extract(windows_server_pattern)
        dataFrame[windows_desktop_columns] = dataFrame[os_column].str.extract(windows_desktop_pattern, flags=re.IGNORECASE)
        # Fill NaN values in the newly created columns with the original 'VM OS' column values
        
        dataFrame['OS Name'] = dataFrame.apply(lambda x: x['Server OS Name'] if pd.isnull(x['OS Name']) else x['OS Name'], axis=1)
        dataFrame['OS Version'] = dataFrame.apply(lambda x: x['Server OS Version'] if pd.isnull(x['OS Version']) else x['OS Version'], axis=1)
        dataFrame['Architecture'] = dataFrame.apply(lambda x: x['Server Architecture'] if pd.isnull(x['Architecture']) else x['Architecture'], axis=1)

        dataFrame['OS Name'] = dataFrame.apply(lambda x: x['Desktop OS Name'] if pd.isnull(x['OS Name']) else x['OS Name'], axis=1)
        dataFrame['OS Version'] = dataFrame.apply(lambda x: x['Desktop OS Version'] if pd.isnull(x['OS Version']) else x['OS Version'], axis=1)
        dataFrame['Architecture'] = dataFrame.apply(lambda x: x['Desktop Architecture'] if pd.isnull(x['Architecture']) else x['Architecture'], axis=1)
        
        dataFrame.drop(windows_server_columns, axis=1, inplace=True)
        dataFrame.drop(windows_desktop_columns, axis=1, inplace=True)
        # Save the modified DataFrame to a CSV file
        dataFrame.to_csv('/tmp/Inventory_VMs_redhat_06_27_24.csv', index=False)
    else:
        print("All columns already exist")
    



def generate_supported_OS_counts(dataFrame, *env_keywords, environment_filter=None):
    """
    Generates a horizontal bar chart displaying the distribution of supported operating systems based on their frequency in the DataFrame.

    Args:
        dataFrame: DataFrame containing OS information.
        *env_keywords: Additional environment keywords.
        environment_filter: Filter for specific environments.

    Returns:
        None
    """

    data_cp = dataFrame.copy()
    if environment_filter and env_keywords:
        data_cp['Environment'] = dataFrame['Environment'].apply(categorize_environment, args=env_keywords)
    
    if environment_filter and environment_filter not in ["all", "both"]:
        data_cp = data_cp[data_cp['Environment'] == environment_filter]
    elif environment_filter == "both":
        data_cp = data_cp.groupby(['OS Name', 'Environment']).size().unstack().fillna(0)
        
    # Calculate the frequency of each unique OS name
    
    if data_cp.empty:
        print(f"None found in {environment_filter} \n")
        return
    # Define specific colors for identified OS names
    supported_os_colors = {
        'Red Hat Enterprise Linux': 'red',
        'SUSE Linux Enterprise': 'green',
        'Microsoft Windows Server': 'navy',
        'Microsoft Windows': 'blue'
        # Add more OS names and colors as needed
    }

    if environment_filter and environment_filter != "both":
        filtered_counts = data_cp['OS Name'].value_counts()
    # If we are looking at both prod/non-prod we don't want an OS Name count
    else:
        filtered_counts = data_cp

    filtered_counts = filtered_counts[filtered_counts.index.isin(supported_os_colors.keys())]
    filtered_counts = filtered_counts.astype(int)

    colors = [supported_os_colors[os] for os in filtered_counts.index]
    # We want to use the official OS colours when there is only 1 bar per os
    if environment_filter and environment_filter != "both":
        filtered_counts.plot(kind='barh', rot=45, color=colors)
    # Remove the color coding if we are comparing both environments as it doesn't look correct
    else:
        filtered_counts.plot(kind='barh', rot=45)
    print(filtered_counts)
    if args.generate_graphs:
        # Set titles and labels for the plot
        if environment_filter not in ['prod', 'non-prod']:
            plt.title('Supported Operating Systems For All Environments')
        else:
            plt.title(f'Supported Operating Systems for {environment_filter.title()}')
        plt.ylabel('Operating Systems')
        plt.xlabel('Count')
        plt.xscale('log')
        plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
        # This sets the ticks on the bottom so that very large numbers can be represented next to smaller numbers while still having a visible bar
        # this is similar to leaving the log scale except it shows the actual number of the smallest and largest bars
        if environment_filter != "both":
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
    if args.minimum_count:
        minimumCount = args.minimum_count
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
    counts = filtered_df['OS Version'].fillna('unknown').value_counts().reset_index()
    counts.columns = ['OS Version', 'Count']

    format_dataframe_output(counts)
    
    # We want to print out a text table and not the dataframe
    if args.minimum_count is not None and args.minimum_count > 0:
        # Filter counts to exclude entries with a count below args.minimum_count
        counts = counts[counts['Count'] >= args.minimum_count]
    # Plot the counts as a horizontal bar chart
    if not counts.empty:
        ax = counts.plot(kind='barh', rot=45)
        if args.generate_graphs:
            # Set titles and labels for the plot
            plt.title(f'Distribution of {os_name}')
            plt.ylabel('OS Version')
            plt.xlabel('Count')

            # Correctly set the x-axis tick labels to display OS Versions
            plt.xticks(rotation=0)  # Adjust rotation as needed
            ax.set_yticklabels(counts['OS Version'])

            plt.show(block=True)
            plt.close()


def calculate_disk_space_ranges(dataFrame, show_disk_in_tb=False):
    """
    Calculates disk space ranges based on the provisioned disk space of virtual machines in the DataFrame.

    Args:
        dataFrame: DataFrame containing disk space information for virtual machines.
        show_disk_in_tb: Boolean flag to determine the disk space ranges (default: False).

    Returns:
        List of disk space ranges with VMs falling within each range.
    """
    frameHeading = column_headers['vmDisk']
    # sometimes the values in this column are interpreted as a string and have a comma inserted
    # we want to check and replace the comma
    for index, row in dataFrame.iterrows():
        # Check if the current element is a string
        if isinstance(row[frameHeading], str):
            # Replace commas in the string
            dataFrame.at[index, frameHeading] = row[frameHeading].replace(',', '')
    dataFrame[frameHeading] = pd.to_numeric(dataFrame[frameHeading], errors='coerce')
    unit = column_headers['unitType']


    # Determine the minimum and maximum disk space provisioned across all VMs
    if unit == "MB":
        min_disk_space = round(int(dataFrame[frameHeading].min())/1024)
        max_disk_space = round(int(dataFrame[frameHeading].max())/1024)
    else:
        min_disk_space = round(int(dataFrame[frameHeading].min()))
        max_disk_space = round(int(dataFrame[frameHeading].max()))
    
    # Define the final range based on the maximum disk space provisioned
    if max_disk_space > 9000:
        final_range = (9001, max_disk_space)
    else:
        final_range = (10001, 15000)
    
    if show_disk_in_tb:
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
        epsilon = 1  # Example epsilon, adjust based on observed precision issues
        if unit == "MB":
            vms_in_range = dataFrame[(dataFrame[frameHeading] / 1024 >= range_start - epsilon) & (dataFrame[frameHeading] / 1024 <= range_end + epsilon)]
        else:
            vms_in_range = dataFrame[(dataFrame[frameHeading] >= range_start - epsilon) & (dataFrame[frameHeading] <= range_end + epsilon)]
        if not vms_in_range.empty:
            disk_space_ranges_with_vms.append((range_start, range_end))
    return disk_space_ranges_with_vms


def plot_disk_space_distribution(dataFrame, os_name=None, os_version=None, show_disk_in_tb=False, frameHeading="VM Provisioned (GB)"):
    """
    Plots the distribution of disk space for virtual machines based on specified criteria.

    Args:
        dataFrame: DataFrame containing disk space information for virtual machines.
        os_name: Name of the operating system (default: None).
        os_version: Version of the operating system (default: None).
        show_disk_in_tb: Boolean flag to filter disk space greater than 2000 GB (default: False).

    Returns:
        None
    """

    # Create a subplot for plotting
    fig, ax = plt.subplots()
    
    # Calculate disk space ranges and update the DataFrame with the corresponding disk space range for each VM
    disk_space_ranges = calculate_disk_space_ranges(dataFrame, show_disk_in_tb=show_disk_in_tb, frameHeading=frameHeading)
    
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
    if pd.isnull(x):
        # if we get a blank environment field assume it's non-prod
        return 'non-prod'
    if not args:
        return 'all envs'
    for arg in args:
        if arg in x:
            return 'prod'
    return 'non-prod'

def sort_attribute_by_environment(dataFrame, *env_keywords, attribute="operatingSystem", os_filter=None, environment_filter=None, show_disk_in_tb=False, frameHeading="VM Provisioned (GB)"):
    """
    Sorts an attribute by environment in the provided DataFrame based on specified filters.

    Args:
        dataFrame: DataFrame containing the data to be sorted.
        *env_keywords: Keywords related to environments.
        attribute: Attribute to sort by (default: "operatingSystem").
        os_filter: Filter for specific operating systems (default: None).
        environment_filter: Filter for specific environments (default: None).

    Returns:
        None
    """
    env_column = "Environment"
    data_cp = dataFrame.copy()
    if env_column not in dataFrame.columns:
        if 'ent-env' in dataFrame.columns:
            env_column = 'ent-env'
        else:
            raise ValueError("Neither 'Environment' nor 'ent-env' found in DataFrame columns.")

    data_cp[env_column] = dataFrame[env_column].apply(categorize_environment, args=env_keywords)

    if os_filter:
        data_cp = data_cp[data_cp['OS Name'] == os_filter]

    if environment_filter and environment_filter not in ["all", "both"]:
        data_cp = data_cp[data_cp[env_column] == environment_filter]

    if data_cp.empty:
        print(f"None found in {environment_filter} \n")
        return

    if attribute == "operatingSystem":
        handle_operating_system(data_cp, environment_filter)
    elif attribute == "diskSpace":
        handle_disk_space(data_cp, environment_filter, env_keywords, os_filter, show_disk_in_tb=show_disk_in_tb)

def handle_operating_system(data_cp, environment_filter):
    """
    Handles operating system information based on the provided data and environment filter.

    Args:
        data_cp: DataFrame containing operating system information for virtual machines.
        environment_filter: Filter for specific environments.

    Returns:
        None
    """
    if args.minimum_count:
        min_count = args.minimum_count
    else:
        min_count = 100

    if not environment_filter or environment_filter == 'all':
        counts = data_cp['OS Name'].value_counts()
        counts = counts[counts >= min_count]
    else:
        counts = data_cp.groupby(['OS Name', 'Environment']).size().unstack().fillna(0)
        counts['total'] = counts.sum(axis=1)
        counts['combined_total'] = counts['prod'] + counts['non-prod']
        counts = counts[(counts['total'] >= min_count) & (counts['combined_total'] >= min_count)].drop(['total', 'combined_total'], axis=1)
        counts = counts.sort_values(by='prod', ascending=False)
    
    print(counts)

    os_names = [idx[1] for idx in counts.index] if counts.index.nlevels == 2 else counts.index
    os_colors = {
        'Red Hat Enterprise Linux': 'red',
        'SUSE Linux Enterprise': 'green',
        'Microsoft Windows Server': 'navy',
        'Microsoft Windows': 'blue',
        "Ubuntu": "orange",
        "Oracle Linux": "maroon",
        "unknown": "grey"
    }

    random_colors = cm.rainbow(np.linspace(0, 1, len(counts)))
    colors = [os_colors.get(os, random_colors[i]) for i, os in enumerate(os_names)]

    ax = counts.plot(kind='barh', rot=45, color=colors)
    if args.generate_graphs:
        plt.xlabel('Count')
        plt.title(f'OS Counts by Environment Type (>= {min_count})')
        plt.show(block=True)

def handle_disk_space(data_cp, environment_filter, env_keywords, os_filter, show_disk_in_tb=False):
    """
    Handles disk space information based on the provided data, environment filter, and operating system filter.

    Args:
        data_cp: DataFrame containing disk space information for virtual machines.
        environment_filter: Filter for specific environments.
        env_keywords: Keywords related to environments.
        os_filter: Filter for specific operating systems.

    Returns:
        None
    """
    diskHeading = column_headers['vmDisk']
    envHeading = column_headers['environment']
    unit = column_headers['unitType']
    disk_space_ranges = calculate_disk_space_ranges(data_cp, show_disk_in_tb=show_disk_in_tb)
    for lower, upper in disk_space_ranges:
        if unit == "MB":
            mask = (round(data_cp[diskHeading] /1024) >= lower) & (round(data_cp[diskHeading] /1024) <= upper)
        else:
            mask = (data_cp[diskHeading] >= lower) & (data_cp[diskHeading] <= upper)
        data_cp.loc[mask, 'Disk Space Range'] = f'{lower}-{upper} GB'

    if environment_filter is None:
        environment_filter = "all"

    if environment_filter == "both":
        range_counts_by_environment = data_cp.groupby(['Disk Space Range', envHeading]).size().unstack(fill_value=0)
    elif environment_filter == "all":
        range_counts_by_environment = data_cp['Disk Space Range'].value_counts().reset_index()
        range_counts_by_environment.columns = ['Disk Space Range', 'Count']
        range_counts_by_environment.set_index('Disk Space Range', inplace=True)
    else:
        range_counts_by_environment = data_cp[data_cp[envHeading] == environment_filter].groupby(['Disk Space Range', envHeading]).size().unstack(fill_value=0)

    # I want to sort the ranges by the number at the end of the range. I need to split out the number and the unit of measurement
    range_counts_by_environment['second_number'] = range_counts_by_environment.index.str.split('-').str[1].str.split().str[0].astype(int)
    sorted_range_counts_by_environment = range_counts_by_environment.sort_values(by='second_number', ascending=True)
    sorted_range_counts_by_environment.drop('second_number', axis=1, inplace=True)

    if os_filter:
        print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords, os_filter=os_filter)
    else:
        print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords)   
    try: 
        sorted_range_counts_by_environment.plot(kind='bar', stacked=False, figsize=(12, 8), rot=45)
    except:
        pass
    if args.generate_graphs:
        plt.xlabel('Disk Space Range')
        plt.ylabel('Number of VMs')
        plt.title(f'VM Disk Size Ranges Sorted by Environment {f"for {os_filter}" if os_filter else ""}')
        plt.show(block=True)

def print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords, os_filter=None):
    """
    Prints formatted disk space information based on the sorted range counts by environment.

    Args:
        sorted_range_counts_by_environment: DataFrame containing sorted range counts by environment.
        environment_filter: Filter for specific environments.
        env_keywords: Keywords related to environments.
        os_filter: Filter for specific operating systems (default: None).

    Returns:
        None
    """

    col_widths = {'Environment': 22, **{env: 10 for env in sorted_range_counts_by_environment.columns}} if env_keywords and environment_filter != "all" else {**{env: 17 for env in sorted_range_counts_by_environment.columns}}
    formatted_rows = []
    if environment_filter == "all":
        formatted_rows.append('Disk Space Range'.ljust(20) + 'Count'.ljust(col_widths['Count']))
        justification = 19
    else:
        justification = 15
    for index, row in sorted_range_counts_by_environment.iterrows():
        formatted_row = [str(index).ljust(justification)]
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
    generic_group.add_argument('--file', type=str, help='The file to parse', required=True)
    generic_group.add_argument('--sort-by-env', type=str, nargs='?', help='Sort disk by environment. Use "all" to get combine count, "both" to show both non-prod and prod, or specify one.')
    generic_group.add_argument('--prod-env-labels', type=str, nargs='?', help="The values in your data that represent prod environments. This is used to generate prod and non-prod stats. Passed as CSV i.e. --prod-env-labels 'baker,dte'")
    generic_group.add_argument('--generate-graphs', action='store_true', help='Choose whether or not to output visual graphs. If this option is not set, a text table will be outputted to the terminal')
    disk_group.add_argument('--get-disk-space-ranges', action='store_true', help="This flag will get disk space ranges regardless of OS. Can be combine with --prod-env-labels and --sort-by-env to target a specific environment")
    disk_group.add_argument('--show-disk-space-by-os', action='store_true', help='Show disk space by OS')
    disk_group.add_argument('--breakdown-by-terabyte', action='store_true', help='Breaks disk space down into 0-2TB, 2-9TB and 9TB+ instead of the default categories')
    os_group.add_argument('--output-os-by-version', action='store_true', help='Output OS by version')
    os_group.add_argument('--get-os-counts', action='store_true', help='Generate a report that counts the inventory broken down by OS')
    os_group.add_argument('--os-name', type=str, help='The name of the Operating System to produce a report about')
    os_group.add_argument('--minimum-count', type=int, help='Anything below this number will be excluded from the results')
    os_group.add_argument('--get-supported-os', action="store_true", help="Display a graph of the supported operating systems for OpenShift Virt")
    os_group.add_argument('--get-unsupported-os', action="store_true", help="Display a graph of the unsupported operating systems for OpenShift Virt")

    args = parser.parse_args()


    def required_if(argument, value):
        """
        Decorator that checks if a specific argument is required based on a given value.

        Args:
            argument: The argument to be checked.
            value: The value that triggers the requirement for the argument.

        Returns:
            A function that validates the argument value.
        """

        def required(argument_value):
            if argument_value == value and getattr(args, argument) is None:
                raise argparse.ArgumentTypeError(f'{argument} is required when using --sort-by-env')
            return argument_value
        return required
    
    args.sort_by_env = required_if('sort_by_env', '--sort-by-env')(args.sort_by_env)

    # Load the CSV file
    file_path = args.file
    #file_path = "/home/stratus/Downloads/SC_Datacenter_Output.csv"
    #file_path = '/home/stratus/temp/Inventory_VMs_redhat_06_27_24_edited.csv'
    file_type = get_file_type(file_path)
    
    
    if args.generate_graphs:
        # If the user wants to see graphs, set the interactive mode on matplotlib
        matplotlib.use('Qt5Agg')

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

    set_column_headings(df)
    columns_to_keep = column_headers.values()
    df = df.drop(columns=df.columns.difference(columns_to_keep))
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

    if args.get_disk_space_ranges:
        if args.sort_by_env == 'all':
            if args.breakdown_by_terabyte:
                sort_attribute_by_environment(df, attribute="diskSpace", environment_filter=args.sort_by_env, show_disk_in_tb=args.breakdown_by_terabyte)
            else:
                sort_attribute_by_environment(df, attribute="diskSpace", environment_filter=args.sort_by_env)
        elif args.sort_by_env:
            if args.get_disk_space_ranges and environments:
                if args.breakdown_by_terabyte:
                    sort_attribute_by_environment(df, environment_filter=args.sort_by_env,  attribute="diskSpace", show_disk_in_tb=args.breakdown_by_terabyte, *environments)
                else:
                    sort_attribute_by_environment(df, environment_filter=args.sort_by_env,  attribute="diskSpace", *environments)
            else:
                print("Failed to determine prod from non-prod environments... Perhaps you did not pass in the --prod-env-labels ?")
                exit()
        else:
            sort_attribute_by_environment(df, attribute="diskSpace", environment_filter="all")

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
    
    if args.get_supported_os:
        if args.prod_env_labels and args.sort_by_env:
            generate_supported_OS_counts(df, *environments, environment_filter=args.sort_by_env)
        else:
            generate_supported_OS_counts(df)
    if args.get_unsupported_os:
        generate_unsupported_OS_counts(df)
        
    ###
    ############# END OPERATING SYSTEM SECTION

    # disk_use_for_environment(df, show_disk_in_tb=True, frameHeading="VM Used (GB)")

    # disk_use_for_environment(df, show_disk_in_tb=False, frameHeading="VM Used (GB)")

    # generate_all_OS_counts(df)
    

