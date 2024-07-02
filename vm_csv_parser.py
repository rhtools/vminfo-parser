

import pandas as pd
import re
import matplotlib
matplotlib.use('TkAgg')  
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('/home/stratus/Documents/RH_Client/GM/Inventory_VMs_redhat_06_27_24_edited.csv')
# df = pd.read_csv('/tmp/Inventory_VMs_redhat_06_27_24.csv')

# Function to add extra columns to a DataFrame based on a regular expression pattern matching VM OS details
def add_extra_columns(dataFrame):
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


# Function to generate a horizontal bar chart showing the distribution of operating systems based on their counts
def generate_OS_counts(dataFrame):
    # Calculate the frequency of each unique OS name
    counts = dataFrame['OS Name'].value_counts()
    
    # Set minimum and maximum thresholds for filtering counts
    min_count_threshold = 5
    max_count_threshold = 65000
    
    # Filter counts within the set thresholds
    filtered_counts = counts[(counts >= min_count_threshold) & (counts <= max_count_threshold)]
    
    # Plot the filtered counts as a horizontal bar chart
    filtered_counts.plot(kind='barh', rot=45)
    
    # Set titles and labels for the plot
    plt.title('Operating System Distribution')
    plt.ylabel('Operating Systems')
    plt.xlabel('Count')
    
    # Save and display the plot
    plt.savefig('output_plot.png')
    plt.show()


# Function to filter and plot the distribution of OS versions for a given OS name
def os_by_version(dataFrame, os_name):
    # Filter rows where the OS name matches the input parameter
    filtered_df = dataFrame[(dataFrame['OS Name'] == os_name)]
    
    # Calculate the frequency of each unique OS version
    counts = filtered_df['OS Version'].value_counts()
    
    # Plot the counts as a horizontal bar chart
    counts.plot(kind='barh', rot=45)
    
    # Print the filtered DataFrame
    print(filtered_df)
    
    # Set titles and labels for the plot
    plt.title(f'Distribution of {os_name}')
    plt.ylabel('OS Version')
    plt.xlabel('Count')
    
    # Save and display the plot
    plt.savefig('output_plot.png')
    plt.show()


# Function to calculate ranges of disk space provisioned for VMs and identify which VMs fall within these ranges
def calculate_disk_space_ranges(dataFrame):
    # Determine the minimum and maximum disk space provisioned across all VMs
    min_disk_space = int(dataFrame['VM Provisioned (GB)'].min())
    max_disk_space = int(dataFrame['VM Provisioned (GB)'].max())
    
    # Define the final range based on the maximum disk space provisioned
    if max_disk_space > 10000:
        final_range = (10001, max_disk_space)
    else:
        final_range = (10001, 15000)
    
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
        (5001, 10000), 
        final_range
    ]
    
    # Identify which VMs fall within each defined range
    disk_space_ranges_with_vms = []
    for range_start, range_end in disk_space_ranges:
        vms_in_range = dataFrame[(dataFrame['VM Provisioned (GB)'] >= range_start) & (dataFrame['VM Provisioned (GB)'] <= range_end)]
        if not vms_in_range.empty:
            disk_space_ranges_with_vms.append((range_start, range_end))
    
    return disk_space_ranges_with_vms


# Function to plot the distribution of disk space provisioned for VMs, optionally filtered by OS name and version
def plot_disk_space_distribution(dataFrame, os_name=None, os_version=None):
    # Create a subplot for plotting
    fig, ax = plt.subplots()
    
    # Calculate disk space ranges and update the DataFrame with the corresponding disk space range for each VM
    disk_space_ranges = calculate_disk_space_ranges(dataFrame)
    
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
    for range_, count in sorted_dict.items():
        if os_name:
            ax.barh(f'{range_[0]}-{range_[1]} GB', count, label=os_name)
        else:
            ax.barh(f'{range_[0]}-{range_[1]} GB', count)
    
    # Set titles and labels for the plot
    ax.set_ylabel('Disk Space Range')
    ax.set_xlabel('Number of Machines')
    if os_name and os_version:
        ax.set_title(f'Hard Drive Space Breakdown for {os_name} {os_version}')
    elif os_name:
        ax.set_title(f'Hard Drive Space Breakdown for {os_name}')
    else:
        ax.set_title('Hard Drive Space Breakdown for Environment')
    
    # Display the plot
    plt.show()


# Function to plot disk usage by OS, optionally filtered by OS version
def disk_use_by_os(dataFrame, os_name, os_version=None):
    # Filter the DataFrame by OS name, and further by OS version if specified
    filtered_df = dataFrame[dataFrame['OS Name'] == os_name]
    if os_version:
        filtered_df = filtered_df[filtered_df['OS Version'] == os_version]
    
    # Call the function to plot disk space distribution for the filtered DataFrame
    plot_disk_space_distribution(filtered_df, os_name, os_version)


# Function to plot disk usage for the entire environment
def disk_use_for_environment(dataFrame):
    # Call the function to plot disk space distribution for the entire DataFrame
    plot_disk_space_distribution(dataFrame)


#os_by_version(df, "CentOS")
# Call the function for each unique OS name in the 'OS Name' dataframe
unique_os_names = df['OS Name'].unique()
print(unique_os_names)
# for os_name in unique_os_names:
#     disk_use_by_os(df, os_name)

disk_use_by_os(df, "CentOS")

disk_use_for_environment(df)



