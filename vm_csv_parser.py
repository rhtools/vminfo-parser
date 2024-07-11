#!/usr/bin/env python3

import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as ticker
import numpy as np

# This program expects a CSV with the following headings
# VM Power,	VM OS,	VM CPU,	VM MEM (GB), VM Provisioned (GB), VM Used (GB),	Environment	
# The add_extra_columns will add OS Name, OS Version and Architecture
# sample data:
#|VM Power	|VM OS		        |VM CPU |VM MEM (GB)|VM Provisioned (GB)|VM Used (GB)|Environment	
#|PoweredOn	|CentOS 4/5 (32-bit)|	2   |	2	    | 82.112 	        |25.831	     |Test
# While it is likely that this format is not standard to your environment, this program should be able to be
# altered slightly to match what your requirements are

# The primary purpose of this script is to aide in the assessment of migration to OpenShift Virtualization

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
    plt.pie(unsupported_counts, labels=unsupported_counts.index, colors=random_colors, autopct='%1.1f%%')
    plt.title('Unsupported Operating System Distribution')

    # Save and display the plot
    plt.show(block=True)
    plt.close()

def generate_all_OS_counts(dataFrame):
    """
    Generates a horizontal bar chart displaying the distribution of operating systems based on their frequency in the DataFrame.

    Args:
        dataFrame: DataFrame containing OS information.

    Returns:
        None
    """
    # Calculate the frequency of each unique OS name
    counts = dataFrame['OS Name'].value_counts()

    # Set minimum and maximum thresholds for filtering counts
    min_count_threshold = 500
    max_count_threshold = 65000
    # Filter counts within the set thresholds
    filtered_counts = counts[(counts >= min_count_threshold) & (counts <= max_count_threshold)]

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
    print(filtered_df)
    # Calculate the frequency of each unique OS version
    #counts = filtered_df['OS Version'].value_counts()
    counts = filtered_df['OS Version'].fillna('unknown').value_counts()
    print(counts)
    # Plot the counts as a horizontal bar chart
    counts.plot(kind='barh', rot=45)
    
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
    print(sorted_dict)
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
        ax.set_title('Hard Drive Space Breakdown for Organization')
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

    for arg in args:
        if arg in x:
            return 'prod'
    return 'non-prod'

def sort_attribute_by_environment(dataFrame, *env_keywords, attribute="operatingSystem", os_filter=None, environment_filter=None):
    """
    Sorts the operating systems in the DataFrame by environment type and generates a bar plot of OS counts by environment type.

    Args:
        dataFrame: DataFrame containing OS information.
        *env_keywords: Variable number of keywords defining a production environment.
        attribute: Attribute to sort by (e.g., "operatingSystem" or "diskSpace").
        os_filter: Filter for specific operating system (e.g., "Microsoft Windows").
        environment_filter: Filter for specific environment (e.g., "prod").

    Returns:
        None
    """

    # Ensure 'Environment' column exists and categorize environments
    dataFrame['Environment'] = dataFrame['Environment'].apply(categorize_environment, args=env_keywords)

    if os_filter:
        print(os_filter)
        dataFrame = dataFrame[dataFrame['OS Name'] == os_filter]

    if environment_filter:
        dataFrame = dataFrame[dataFrame['Environment'] == environment_filter]

    if attribute == "operatingSystem":
        # Group by 'OS Name' and 'Environment', count occurrences, and unstack
        os_counts = dataFrame.groupby(['OS Name', 'Environment']).size().unstack(fill_value=0)
        print(os_counts)
        # Filter rows where the total count across all OS Names is greater than or equal to 100
        # Calculate total counts per OS Name
        total_counts = os_counts.sum(axis=1).reset_index(name='Total')

        # Merge DataFrames based on OS Name (include all columns)
        filtered_os_counts = os_counts.merge(total_counts, how='left', on='OS Name')

        # Filter for OS Names with total count >= 100
        filtered_os_counts = filtered_os_counts[filtered_os_counts['Total'] >= 100]
        filtered_os_counts = filtered_os_counts.sort_values(by='Total', ascending=False)
        filtered_os_counts.drop('Total', axis=1).plot(kind='barh', x='OS Name', figsize=(10, 6), rot=45)
        print(filtered_os_counts)
        plt.xlabel('Count')
        plt.title('OS Counts by Environment Type (>= 100)')

    if attribute == "diskSpace":
        # Calculate disk space ranges based on the provisioned disk space of virtual machines
        disk_space_ranges = calculate_disk_space_ranges(dataFrame)

        # Filter machines based on disk space condition
        for lower, upper in disk_space_ranges:
            mask = (dataFrame['VM Provisioned (GB)'] >= lower) & (dataFrame['VM Provisioned (GB)'] <= upper)
            dataFrame.loc[mask, 'Disk Space Range'] = f'{lower}-{upper} GB'

        # Count the number of VMs in each disk space range based on environment
        range_counts_by_environment = dataFrame.groupby(['Disk Space Range', 'Environment']).size().unstack(fill_value=0)

        # Sort the disk space ranges in ascending order
        range_counts_by_environment = range_counts_by_environment.reindex(sorted(range_counts_by_environment.index, key=lambda x: int(x.split('-')[0])))
        print(range_counts_by_environment)
        # Plot the bar chart for VMs in specific disk size ranges sorted by environment
        range_counts_by_environment.plot(kind='bar', stacked=False, figsize=(12, 8), rot=45)

        # Add labels and title for clarity
        plt.xlabel('Disk Space Range')
        plt.ylabel('Number of VMs')
        plt.title('VM Disk Size Ranges Sorted by Environment')
        if os_filter:
            plt.title('VM Disk Size Ranges for %s' % os_filter)

    # Display the plot
    plt.show(block=True)
    plt.close()


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
    # Load the CSV file
    df = pd.read_csv('/home/stratus/temp/Inventory_VMs_redhat_06_27_24_edited.csv')
    add_extra_columns(df)
    calculate_average_ram(df, "test")
    
    # Call the function for each unique OS name in the 'OS Name' dataframe
    unique_os_names = df['OS Name'].unique()

    for os_name in unique_os_names:
        disk_use_by_os(df, os_name)

    for os_name in unique_os_names:
        os_by_version(df, os_name)

    sort_attribute_by_environment(df, "test", attribute="diskSpace", os_filter="Red Hat Enterprise Linux", environment_filter="prod")

    os_by_version(df, "Microsoft Windows")

    disk_use_for_environment(df, filter_diskspace=True, frameHeading="VM Used (GB)")

    disk_use_for_environment(df, filter_diskspace=False, frameHeading="VM Used (GB)")

    generate_all_OS_counts(df)
    generate_supported_OS_counts(df)
    generate_unsupported_OS_counts(df)

