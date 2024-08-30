# vm_csv_parser.py

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as ticker
import numpy as np
import re
import argparse
import os
import magic

class Config:
    def __init__(self):
        self.args = None
    
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Process VM CSV file')
        parser.add_argument('--file', type=str, help='The file to parse', required=True)
        parser.add_argument('--sort-by-env', type=str, nargs='?', help='Sort disk by environment. Use "all" to get combine count, "both" to show both non-prod and prod, or specify one.')
        parser.add_argument('--prod-env-labels', type=str, nargs='?', help="The values in your data that represent prod environments. This is used to generate prod and non-prod stats. Passed as CSV i.e. --prod-env-labels 'baker,dte'")
        parser.add_argument('--generate-graphs', action='store_true', help='Choose whether or not to output visual graphs. If this option is not set, a text table will be outputted to the terminal')
        parser.add_argument('--get-disk-space-ranges', action='store_true', help="This flag will get disk space ranges regardless of OS. Can be combine with --prod-env-labels and --sort-by-env to target a specific environment")
        parser.add_argument('--show-disk-space-by-os', action='store_true', help='Show disk space by OS')
        parser.add_argument('--breakdown-by-terabyte', action='store_true', help='Breaks disk space down into 0-2TB, 2-9TB and 9TB+ instead of the default categories')
        parser.add_argument('--over-under-tb', action='store_true', help='A simple break down of machines under 1TB and those over 1TB')
        parser.add_argument('--output-os-by-version', action='store_true', help='Output OS by version')
        parser.add_argument('--get-os-counts', action='store_true', help='Generate a report that counts the inventory broken down by OS')
        parser.add_argument('--os-name', type=str, help='The name of the Operating System to produce a report about')
        parser.add_argument('--minimum-count', type=int, help='Anything below this number will be excluded from the results')
        parser.add_argument('--get-supported-os', action="store_true", help="Display a graph of the supported operating systems for OpenShift Virt")
        parser.add_argument('--get-unsupported-os', action="store_true", help="Display a graph of the unsupported operating systems for OpenShift Virt")
        self.args = parser.parse_args()
    
    def load_from_file(self, file_path):
        # Implement loading configuration from file
        pass
    
    def load_from_env(self):
        # Implement loading configuration from environment variables
        pass

class VMData:
    def __init__(self, df):
        self.df = df
        self.column_headers = {}
    
    @classmethod
    def get_file_type(cls, file_path):
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
        
    @classmethod
    def from_file(cls, file_path):
        file_type = cls.get_file_type(file_path)
        if "csv" in file_type:
            df = pd.read_csv(file_path)
        elif "spreadsheetml" in file_type:
            df = pd.read_excel(file_path)
        else:
            print("File passed in was neither a CSV nor an Excel file\nBailing...")
            exit()
        return cls(df)
    
    def set_column_headings(self):
        version1_columns = {"operatingSystem": "VM OS", "environment": "Environment", "vmMemory": 'VM MEM (GB)', "vmDisk": 'VM Provisioned (GB)'}
        version2_columns = {"operatingSystem": "OS according to the configuration file", "environment": "ent-env", "vmMemory": 'Memory', "vmDisk": 'Total disk capacity MiB'}
        
        if all(col in self.df.columns for col in version1_columns.values()):
            print("\nAll version 1 columns are present in the DataFrame.\n")
            self.column_headers = version1_columns
            self.column_headers["unitType"] = 'GB'
        elif all(col in self.df.columns for col in version2_columns.values()):
            print("\nAll version 2 columns are present in the DataFrame.\n")
            self.column_headers = version2_columns
            self.column_headers["unitType"] = 'MB'
        else:
            print(f"Missing column headers from either {version1_columns.values} or {version2_columns.values}")
            raise ValueError("Headers don't match either of the versions expected")
    
    def add_extra_columns(self):
        os_column = self.column_headers['operatingSystem']
        windows_server_columns = ['Server OS Name', 'Server OS Version', 'Server Architecture']
        windows_desktop_columns = ['Desktop OS Name', 'Desktop OS Version', 'Desktop Architecture']
        
        if not all(col in self.df.columns for col in ['OS Name', 'OS Version', 'Architecture']):
            exclude_windows_pattern = r"^(?!.*Microsoft)(?P<OS_Name>.*?)(?:\s+(?P<OS_Version>\d+(?:/\d+)*\s*(?:or later)?\s*)?\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\))"
            windows_server_pattern = r"^(?P<OS_Name>Microsoft Windows Server)\s+(?P<OS_Version>\d+(?:\.\d+)*(?:\s*R\d+)?(?:\s*SP\d+)?)(?:\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\))?"
            windows_desktop_pattern = r"^(?P<OS_Name>Microsoft Windows)\s+(?!Server)(?P<OS_Version>XP Professional|\d+(?:\.\d+)*|Vista|7|8|10)\s*\((?P<Architecture>.*?64-bit|.*?32-bit)\)"
            
            self.df[['OS Name', 'OS Version', 'Architecture']] = self.df[os_column].str.extract(exclude_windows_pattern)
            self.df[windows_server_columns] = self.df[os_column].str.extract(windows_server_pattern)
            self.df[windows_desktop_columns] = self.df[os_column].str.extract(windows_desktop_pattern, flags=re.IGNORECASE)
            
            self.df['OS Name'] = self.df['Server OS Name'].where(self.df['OS Name'].isnull(), self.df['OS Name'])
            self.df['OS Version'] = self.df['Server OS Version'].where(self.df['OS Version'].isnull(), self.df['OS Version'])
            self.df['Architecture'] = self.df['Server Architecture'].where(self.df['Architecture'].isnull(), self.df['Architecture'])
            
            self.df['OS Name'] = self.df['Desktop OS Name'].where(self.df['OS Name'].isnull(), self.df['OS Name'])
            self.df['OS Version'] = self.df['Desktop OS Version'].where(self.df['OS Version'].isnull(), self.df['OS Version'])
            self.df['Architecture'] = self.df['Desktop Architecture'].where(self.df['Architecture'].isnull(), self.df['Architecture'])
            
            self.df.drop(windows_server_columns + windows_desktop_columns, axis=1, inplace=True)
        else:
            print("All columns already exist")
        
        self.save_to_csv("/tmp/my_file.csv")
    
    def save_to_csv(self, path):
        self.df.to_csv(path, index=False)

class Analyzer:
    def __init__(self, vm_data, parser_args, column_headers=None):
        self.vm_data = vm_data
        self.args = parser_args
        self.column_headers = column_headers

    def calculate_average_ram(self, environment_type):
        os_values = self.vm_data.df['OS Name'].unique()
        
        print("{:<20} {:<10}".format("OS", "Average RAM (GB)"))
        print("-" * 30)
        
        for os in os_values:
            filtered_hosts = self.vm_data.df[(self.vm_data.df['OS Name'] == os) & (self.vm_data.df['Environment'].str.contains(environment_type))]
            
            if not filtered_hosts.empty:
                avg_ram = filtered_hosts[self.column_headers['vmMemory']].mean()
                print("{:<20} {:<10.2f}".format(os, avg_ram))

    def calculate_disk_space_ranges(self, dataFrame=None, show_disk_in_tb=False, over_under_tb=False):
        if dataFrame is None:
            # default to the dataframe in the attribute unless overridden
            dataFrame = self.vm_data.df
        frameHeading = self.column_headers['vmDisk']
        
        # sometimes the values in this column are interpreted as a string and have a comma inserted
        # we want to check and replace the comma
        for index, row in dataFrame.iterrows():
            if isinstance(row[frameHeading], str):
                dataFrame.at[index, frameHeading] = row[frameHeading].replace(',', '')
        
        dataFrame[frameHeading] = pd.to_numeric(dataFrame[frameHeading], errors='coerce')
        unit = self.column_headers['unitType']
        
        min_disk_space = round(int(dataFrame[frameHeading].min()))
        max_disk_space = round(int(dataFrame[frameHeading].max()))
        
        final_range = (9001, max_disk_space) if max_disk_space > 9000 else (10001, 15000)
        
        if show_disk_in_tb:
            disk_space_ranges = [(min_disk_space, 2000), (2001, 9000), final_range]
        elif over_under_tb:
            disk_space_ranges = [(min_disk_space, 1000), (1001, max_disk_space)]
        else:
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
        
        disk_space_ranges_with_vms = []
        for range_start, range_end in disk_space_ranges:
            epsilon = 1  
            if unit == "MB":
                vms_in_range = dataFrame[(dataFrame[frameHeading] / 1024 >= range_start - epsilon) & (dataFrame[frameHeading] / 1024 <= range_end + epsilon)]
            else:
                vms_in_range = dataFrame[(dataFrame[frameHeading] >= range_start - epsilon) & (dataFrame[frameHeading] <= range_end + epsilon)]
            
            if not vms_in_range.empty:
                disk_space_ranges_with_vms.append((range_start, range_end))
        
        return disk_space_ranges_with_vms

    def categorize_environment(self, x, *args):
        if pd.isnull(x):
            return 'non-prod'

        if not args:
            return 'all envs'

        # Ensure x is a string
        if isinstance(x, str):
            for arg in args:
                if arg in x:
                    return 'prod'

        return 'non-prod'


    def format_dataframe_output(self, dataFrame, os_name=None):
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

    def handle_disk_space(self, dataFrame, environment_filter, env_keywords, os_filter=None, show_disk_in_tb=False, over_under_tb=False):
        # NOTE: I am taking in the dataFrame as it is a mutated copy of the original dataFrame stored in self.vmdata.df
        # This copy has a paired down version of the information and then environments have been changed to prod/non-prod
        diskHeading = self.column_headers['vmDisk']
        envHeading = self.column_headers['environment']
        unit = self.column_headers['unitType']
        
        disk_space_ranges = self.calculate_disk_space_ranges(dataFrame=dataFrame, show_disk_in_tb=show_disk_in_tb, over_under_tb=over_under_tb)
        
        for lower, upper in disk_space_ranges:
            if unit == "MB":
                mask = (round(dataFrame[diskHeading] /1024) >= lower) & (round(dataFrame[diskHeading] /1024) <= upper)
            else:
                mask = (dataFrame[diskHeading] >= lower) & (dataFrame[diskHeading] <= upper)
            
            dataFrame.loc[mask, 'Disk Space Range'] = f'{lower}-{upper} GB'
        
        if environment_filter is None:
            environment_filter = "all"
        
        if environment_filter == "both":
            range_counts_by_environment = dataFrame.groupby(['Disk Space Range', envHeading]).size().unstack(fill_value=0)
        elif environment_filter == "all":
            range_counts_by_environment = dataFrame['Disk Space Range'].value_counts().reset_index()
            range_counts_by_environment.columns = ['Disk Space Range', 'Count']
            range_counts_by_environment.set_index('Disk Space Range', inplace=True)
        else:
            range_counts_by_environment = dataFrame[dataFrame[envHeading] == environment_filter].groupby(['Disk Space Range', envHeading]).size().unstack(fill_value=0)
        
        range_counts_by_environment['second_number'] = range_counts_by_environment.index.str.split('-').str[1].str.split().str[0].astype(int)
        sorted_range_counts_by_environment = range_counts_by_environment.sort_values(by='second_number', ascending=True)
        sorted_range_counts_by_environment.drop('second_number', axis=1, inplace=True)
        
        if os_filter:
            self.print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords, os_filter=os_filter)
        else:
            self.print_formatted_disk_space(sorted_range_counts_by_environment, environment_filter, env_keywords)
        
        try:
            sorted_range_counts_by_environment.plot(kind='bar', stacked=False, figsize=(12, 8), rot=45)
        except:
            pass
        
        if self.args.generate_graphs:
            plt.xlabel('Disk Space Range')
            plt.ylabel('Number of VMs')
            plt.title(f'VM Disk Size Ranges Sorted by Environment {f"for {os_filter}" if os_filter else ""}')
            plt.show(block=True)


    def handle_operating_system(self, environment_filter: str, dataFrame: pd.DataFrame = None) -> None:
        if dataFrame is None:
            dataFrame = self.vm_data.df        
        
        min_count = self.args.minimum_count if self.args.minimum_count else 100
        if isinstance(environment_filter, pd.DataFrame):
            environment_filter = str(environment_filter)
            
        if not environment_filter or environment_filter == 'all':
            counts = dataFrame['OS Name'].value_counts()
            counts = counts[counts >= min_count]
        else:
            counts = dataFrame.groupby(['OS Name', 'Environment']).size().unstack().fillna(0)
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
            "Ubuntu Linux": "orange",
            "Oracle Linux": "maroon",
            "unknown": "grey"
        }
        
        random_colors = cm.rainbow(np.linspace(0, 1, len(counts)))
        colors = [os_colors.get(os, random_colors[i]) for i, os in enumerate(os_names)]
        
        ax = counts.plot(kind='barh', rot=45, color=colors)
        
        if self.args.generate_graphs:
            plt.xlabel('Count')
            plt.title(f'OS Counts by Environment Type (>= {min_count})')
            plt.show(block=True)

    def generate_all_OS_counts(self, minimumCount=500, maximumCount=99999):
        counts = self.vm_data.df['OS Name'].value_counts()
        if self.args.minimum_count:
            minimumCount = self.args.minimum_count
        
        filtered_counts = counts[(counts >= minimumCount) & (counts <= maximumCount)]
        
        os_colors = {
            'Red Hat Enterprise Linux': 'red',
            'SUSE Linux Enterprise': 'green',
            'Microsoft Windows Server': 'navy',
            'Microsoft Windows': 'blue',
            "Ubuntu Linux": "orange",
            "Oracle Linux": "maroon",
            "unknown": "grey"
        }
        
        random_colors = cm.rainbow(np.linspace(0, 1, len(filtered_counts)))
        colors = [os_colors.get(os, random_colors[i]) for i, os in enumerate(filtered_counts.index)]
        
        filtered_counts.plot(kind='barh', rot=45, color=colors)
        print(filtered_counts)
        
        if self.args.generate_graphs:
            plt.title('Operating System Distribution')
            plt.ylabel('Operating Systems')
            plt.xlabel('Count')
            plt.xscale('log')
            plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
            plt.xticks([filtered_counts.iloc[0] - (filtered_counts.iloc[0] % 100), filtered_counts.iloc[len(filtered_counts)//2] - (filtered_counts.iloc[len(filtered_counts)//2] % 100), filtered_counts.iloc[-1]])

    
        data_cp = dataFrame.copy()
        if environment_filter and env_keywords:
            data_cp['Environment'] = dataFrame['Environment'].apply(self.categorize_environment, args=env_keywords)
        
        if environment_filter and environment_filter not in ["all", "both"]:
            data_cp = data_cp[data_cp['Environment'] == environment_filter]
        elif environment_filter == "both":
            data_cp = data_cp.groupby(['OS Name', 'Environment']).size().unstack().fillna(0)
        
        if data_cp.empty:
            print(f"None found in {environment_filter} \n")
            return
        
        supported_os_colors = {
            'Red Hat Enterprise Linux': 'red',
            'SUSE Linux Enterprise': 'green',
            'Microsoft Windows Server': 'navy',
            'Microsoft Windows': 'blue'
        }
        
        if environment_filter and environment_filter != "both":
            filtered_counts = data_cp['OS Name'].value_counts()
        else:
            filtered_counts = data_cp
        
        filtered_counts = filtered_counts[filtered_counts.index.isin(supported_os_colors.keys())]
        filtered_counts = filtered_counts.astype(int)
        
        colors = [supported_os_colors[os] for os in filtered_counts.index]
        
        if environment_filter and environment_filter != "both":
            filtered_counts.plot(kind='barh', rot=45, color=colors)
        else:
            filtered_counts.plot(kind='barh', rot=45)
        
        print(filtered_counts)
        
        if self.args.generate_graphs:
            if environment_filter not in ['prod', 'non-prod']:
                plt.title('Supported Operating Systems For All Environments')
            else:
                plt.title(f'Supported Operating Systems for {environment_filter.title()}')
            
            plt.ylabel('Operating Systems')
            plt.xlabel('Count')
            plt.xscale('log')
            plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
            
            if environment_filter != "both":
                plt.xticks([filtered_counts.iloc[0] - (filtered_counts.iloc[0] % 100), filtered_counts.iloc[len(filtered_counts)//2] - (filtered_counts.iloc[len(filtered_counts)//2] % 100), filtered_counts.iloc[-1]])
            
            plt.show(block=True)
            plt.close()

 
    def generate_supported_OS_counts(self, *env_keywords, environment_filter=None):
        data_cp = self.vm_data.df.copy()
        if environment_filter and env_keywords:
            data_cp['Environment'] = self.vm_data.df['Environment'].apply(self.categorize_environment, args=env_keywords)
        
        if environment_filter and environment_filter not in ["all", "both"]:
            data_cp = data_cp[data_cp['Environment'] == environment_filter]
        elif environment_filter == "both":
            data_cp = data_cp.groupby(['OS Name', 'Environment']).size().unstack().fillna(0)
        
        if data_cp.empty:
            print(f"None found in {environment_filter} \n")
            return
        
        supported_os_colors = {
            'Red Hat Enterprise Linux': 'red',
            'SUSE Linux Enterprise': 'green',
            'Microsoft Windows Server': 'navy',
            'Microsoft Windows': 'blue'
        }
        
        if environment_filter and environment_filter != "both":
            filtered_counts = data_cp['OS Name'].value_counts()
        else:
            filtered_counts = data_cp
        
        filtered_counts = filtered_counts[filtered_counts.index.isin(supported_os_colors.keys())]
        filtered_counts = filtered_counts.astype(int)
        
        colors = [supported_os_colors[os] for os in filtered_counts.index]
        
        print(filtered_counts)
        
        if self.args.generate_graphs:
            if environment_filter and environment_filter != "both":
                filtered_counts.plot(kind='barh', rot=45, color=colors)
            else:
                filtered_counts.plot(kind='barh', rot=45)
            if environment_filter not in ['prod', 'non-prod']:
                plt.title('Supported Operating Systems For All Environments')
            else:
                plt.title(f'Supported Operating Systems for {environment_filter.title()}')
            
            plt.ylabel('Operating Systems')
            plt.xlabel('Count')
            plt.xscale('log')
            plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
            
            if environment_filter != "both":
                plt.xticks([filtered_counts.iloc[0] - (filtered_counts.iloc[0] % 100), filtered_counts.iloc[len(filtered_counts)//2] - (filtered_counts.iloc[len(filtered_counts)//2] % 100), filtered_counts.iloc[-1]])
            
            plt.show(block=True)
            plt.close()

    def generate_unsupported_OS_counts(self):
        counts = self.vm_data.df['OS Name'].value_counts()
        
        supported_os = ['Red Hat Enterprise Linux', 'SUSE Linux Enterprise', 'Microsoft Windows Server', 'Microsoft Windows']
        
        unsupported_counts = counts[~counts.index.isin(supported_os)]
        
        threshold = 0.0075
        other_counts = unsupported_counts[unsupported_counts / unsupported_counts.sum() < threshold]
        other_total = other_counts.sum()
        unsupported_counts = unsupported_counts[~unsupported_counts.index.isin(other_counts.index)]
        unsupported_counts['Other'] = other_total
        
        print(unsupported_counts)
        
        if self.args.generate_graphs:
            random_colors = cm.rainbow(np.linspace(0, 1, len(unsupported_counts)))
            plt.pie(unsupported_counts, labels=unsupported_counts.index, colors=random_colors, autopct='%1.1f%%')
            plt.title('Unsupported Operating System Distribution')
            
            plt.show(block=True)
            plt.close()

    def os_by_version(self, os_name):
        filtered_df = self.vm_data.df[(self.vm_data.df['OS Name'] == os_name)]
        counts = filtered_df['OS Version'].fillna('unknown').value_counts().reset_index()
        counts.columns = ['OS Version', 'Count']
        
        self.format_dataframe_output(counts, os_name=os_name)
        
        if self.args.minimum_count is not None and self.args.minimum_count > 0:
            counts = counts[counts['Count'] >= self.args.minimum_count]
        
        if not counts.empty:
            ax = counts.plot(kind='barh', rot=45)
            
            if self.args.generate_graphs:
                plt.title(f'Distribution of {os_name}')
                plt.ylabel('OS Version')
                plt.xlabel('Count')
                
                plt.xticks(rotation=0)  
                ax.set_yticklabels(counts['OS Version'])
                
                plt.show(block=True)
                plt.close()

    def print_formatted_disk_space(self, sorted_range_counts_by_environment, environment_filter, env_keywords, os_filter=None):
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

    def plot_disk_space_distribution(self, os_name=None, os_version=None, show_disk_in_tb=False):
        """
        Plots the distribution of disk space for virtual machines based on specified criteria.

        Args:
            os_name: Name of the operating system (default: None).
            os_version: Version of the operating system (default: None).
            show_disk_in_tb: Boolean flag to filter disk space greater than 2000 GB (default: False).
            frameHeading: Column header for disk space (default: "VM Provisioned (GB)").

        Returns:
            None
        """
        # Create a subplot for plotting
        fig, ax = plt.subplots()

        # Calculate disk space ranges and update the DataFrame with the corresponding disk space range for each VM
        disk_space_ranges = self.calculate_disk_space_ranges(show_disk_in_tb=show_disk_in_tb)

        column_name = self.vm_data.column_headers['vmDisk']
        # Filter machines based on disk space condition
        for lower, upper in disk_space_ranges:
            mask = (self.vm_data.df[column_name] >= lower) & (self.vm_data.df[column_name] <= upper)
            self.vm_data.df.loc[mask, 'Disk Space Range'] = f'{lower}-{upper} GB'

        # Count the number of VMs in each disk space range
        range_counts = {range_: 0 for range_ in disk_space_ranges}
        for lower, upper in disk_space_ranges:
            mask = (self.vm_data.df[column_name]  >= lower) & (self.vm_data.df[column_name]  <= upper)
            count = self.vm_data.df.loc[mask].shape[0]
            range_counts[(lower, upper)] = count

        # Sort the counts and plot them as a horizontal bar chart
        sorted_dict = dict(sorted(range_counts.items(), key=lambda x: x[1]))

        # Print the disk space ranges and counts
        print("Disk Space Range (GB)\t\tCount")
        for disk_range in range_counts.items():
            disk_range_str = f"{disk_range[0][0]}-{disk_range[0][1]}"
            print(f"{disk_range_str.ljust(32)} {disk_range[1]}")

        if self.args.generate_graphs:
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
            
    def sort_attribute_by_environment(self, *env_keywords, attribute="operatingSystem", os_filter=None, environment_filter=None, show_disk_in_tb=False, over_under_tb=False, frameHeading="VM Provisioned (GB)"):
        env_column = "Environment"
        data_cp = self.vm_data.df.copy()
        
        if env_column not in self.vm_data.df.columns:
            if 'ent-env' in self.vm_data.df.columns:
                env_column = 'ent-env'
            else:
                raise ValueError("Neither 'Environment' nor 'ent-env' found in DataFrame columns.")
        
        data_cp[env_column] = self.vm_data.df[env_column].apply(self.categorize_environment, args=env_keywords)
        
        if os_filter:
            data_cp = data_cp[data_cp['OS Name'] == os_filter]
        
        if environment_filter and environment_filter not in ["all", "both"]:
            data_cp = data_cp[data_cp[env_column] == environment_filter]
        
        if data_cp.empty:
            print(f"None found in {environment_filter} \n")
            return
        
        if attribute == "operatingSystem":
            self.handle_operating_system(environment_filter, dataFrame=data_cp)
        elif attribute == "diskSpace":
            self.handle_disk_space(data_cp, environment_filter, env_keywords, os_filter, show_disk_in_tb=show_disk_in_tb, over_under_tb=over_under_tb)
            #handle_disk_space(self, environment_filter, env_keywords, os_filter=None, show_disk_in_tb=False, over_under_tb=False):

class Visualizer:
    def __init__(self, analyzer):
        self.analyzer = analyzer
    
    def visualize_disk_space(self):
        disk_space_ranges = self.analyzer.calculate_disk_space_ranges()
        
        # Count the number of VMs in each disk space range
        range_counts = {range_: 0 for range_ in disk_space_ranges}
        for lower, upper in disk_space_ranges:
            mask = (self.analyzer.vm_data.df[self.analyzer.vm_data.column_headers['vmDisk']] >= lower) & (self.analyzer.vm_data.df[self.analyzer.vm_data.column_headers['vmDisk']] <= upper)
            count = self.analyzer.vm_data.df.loc[mask].shape[0]
            range_counts[(lower, upper)] = count
        
        # Sort the counts and plot them as a horizontal bar chart
        sorted_dict = dict(sorted(range_counts.items(), key=lambda x: x[1]))
        print("Disk Space Range (GB)\t\tCount")
        for disk_range in range_counts.items():
            # The first indexed item is a tuple that represents the disk space range
            # so we need to take the first and the second number and convert it to a str
            # for better printing
            disk_range_str = f"{disk_range[0][0]}-{disk_range[0][1]}"
            print(f"{disk_range_str.ljust(32)} {disk_range[1]}")
        
        if self.analyzer.vm_data.df.empty:
            print("No data to plot")
            return
        
        # Create a subplot for plotting
        fig, ax = plt.subplots()
        
        # Plot the sorted counts as a horizontal bar chart
        for range_, count in sorted_dict.items():
            ax.barh(f'{range_[0]}-{range_[1]} GB', count)
        
        # Set titles and labels for the plot
        ax.set_ylabel('Disk Space Range')
        ax.set_xlabel('Number of VMs')
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        
        ax.set_title('Hard Drive Space Breakdown for All Environments')
        
        ax.set_xlim(right=max(range_counts.values()) + 1.5)
        
        # Display the plot
        plt.show(block=True)
        plt.close()
    
    def visualize_os_distribution(self):
        os_column = self.analyzer.vm_data.column_headers['operatingSystem']
        env_column = 'Environment'
        
        # Calculate the frequency of each unique OS name
        counts = self.analyzer.vm_data.df['OS Name'].value_counts()
        
        # Define specific colors for identified OS names
        os_colors = {
            'Red Hat Enterprise Linux': 'red',
            'SUSE Linux Enterprise': 'green',
            'Microsoft Windows Server': 'navy',
            'Microsoft Windows': 'blue',
            "Ubuntu Linux": "orange",
            "Oracle Linux": "maroon",
            "unknown": "grey"
            # Add more OS names and colors as needed
        }
        
        # Generate random colors for bars not in supported_os_colors
        random_colors = cm.rainbow(np.linspace(0, 1, len(counts)))
        colors = [os_colors.get(os, random_colors[i]) for i, os in enumerate(counts.index)]
        
        # Plot the counts as a horizontal bar chart with specified and random colors
        counts.plot(kind='barh', rot=45, color=colors)
        
        print(counts)
        
        if self.analyzer.vm_data.df.empty:
            print("No data to plot")
            return
        
        # Set titles and labels for the plot
        plt.title('Operating System Distribution')
        plt.ylabel('Operating Systems')
        plt.xlabel('Count')
        plt.xscale('log')
        plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())
        
        plt.xticks([counts.iloc[0] - (counts.iloc[0] % 100), counts.iloc[len(counts)//2] - (counts.iloc[len(counts)//2] % 100), counts.iloc[-1]])
        
        # Display the plot
        plt.show(block=True)
        plt.close()

def main():
    config = Config()
    config.parse_arguments()
    
    vm_data = VMData.from_file(config.args.file)
    vm_data.set_column_headings()
    vm_data.add_extra_columns()
    
    analyzer = Analyzer(vm_data, config.args, column_headers=vm_data.column_headers)
    visualizer = Visualizer(analyzer)
    
    # Load environments from prod-env-labels if provided
    environments = []
    if config.args.prod_env_labels:
        environments = config.args.prod_env_labels.split(',')
    
    # Check if environments are defined for sorting
    if config.args.sort_by_env and not environments:
        print("\n\nYou specified you wanted to sort by environment but did not provide a definition of what categorizes a Prod environment... exiting\n")
        exit()
    
    # Perform analysis and visualization based on config.args
    if config.args.get_disk_space_ranges:
        analyzer.calculate_disk_space_ranges(config.args.breakdown_by_terabyte, config.args.over_under_tb)
        #visualizer.visualize_disk_space()
    
    if config.args.show_disk_space_by_os:
        if config.args.os_name:
            # If the user specifies an OS, use that to filter out everything else
            if environments:
                if config.args.sort_by_env:
                    analyzer.plot_disk_space_distribution(os_name=config.args.os_name, environment_filter=config.args.sort_by_env, show_disk_in_tb=config.args.breakdown_by_terabyte)
                else:
                    analyzer.plot_disk_space_distribution(os_name=config.args.os_name, show_disk_in_tb=config.args.breakdown_by_terabyte)
            else:
                analyzer.plot_disk_space_distribution(os_name=config.args.os_name, show_disk_in_tb=config.args.breakdown_by_terabyte)
        else:
            # If the user has not specified an OS name, assume they want them all
            for os_name in vm_data.df['OS Name'].unique():
                if environments:                  
                    #analyzer.plot_disk_space_distribution(os_name=os_name, show_disk_in_tb=config.args.breakdown_by_terabyte)
                    analyzer.sort_attribute_by_environment(attribute="diskSpace", os_filter=os_name,environment_filter=config.args.sort_by_env, over_under_tb=config.args.over_under_tb, *environments)

                else:
                    if config.args.over_under_tb:
                        analyzer.sort_attribute_by_environment(os_name=os_name, show_disk_in_tb=config.args.breakdown_by_terabyte)
                    else:                            
                        analyzer.sort_attribute_by_environment(os_name=os_name)
    
    if config.args.get_disk_space_ranges:
        if config.args.sort_by_env == 'all':
            analyzer.calculate_disk_space_ranges(config.args.breakdown_by_terabyte, config.args.over_under_tb)
            #visualizer.visualize_disk_space()
        elif config.args.sort_by_env:
            if config.args.get_disk_space_ranges and environments:
                analyzer.calculate_disk_space_ranges(config.args.breakdown_by_terabyte, config.args.over_under_tb)
                #visualizer.visualize_disk_space()
            else:
                print("Failed to determine prod from non-prod environments... Perhaps you did not pass in the --prod-env-labels ?")
                exit()
        else:
            analyzer.calculate_disk_space_ranges(config.args.breakdown_by_terabyte, config.args.over_under_tb)
            #visualizer.visualize_disk_space()
    
    if config.args.get_os_counts:
        if environments:
            if config.args.os_name:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem", os_filter=config.args.os_name, *environments)
                # visualizer.visualize_os_distribution()
            elif config.args.sort_by_env:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem", *environments, environment_filter=config.args.sort_by_env)
                # visualizer.visualize_os_distribution()
            else:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem", *environments)
                # visualizer.visualize_os_distribution()
        else:
            if config.args.os_name:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem", os_filter=config.args.os_name)
                # visualizer.visualize_os_distribution()
            else:
                analyzer.sort_attribute_by_environment(attribute="operatingSystem")
                ###
                # visualizer.visualize_os_distribution()
    
    if config.args.output_os_by_version:
        for os_name in vm_data.df['OS Name'].unique():
            analyzer.os_by_version(os_name)
    
    if config.args.get_supported_os:
        if config.args.prod_env_labels and config.args.sort_by_env:
            analyzer.generate_supported_OS_counts(*config.args.prod_env_labels.split(','), environment_filter=config.args.sort_by_env)
            #generate_supported_OS_counts(df, *environments, environment_filter=args.sort_by_env)

            # visualizer.visualize_os_distribution()
        else:
            analyzer.generate_supported_OS_counts(environment_filter=config.args.sort_by_env)
            # visualizer.visualize_os_distribution()
    
    if config.args.get_unsupported_os:
        analyzer.generate_unsupported_OS_counts()
        # visualizer.visualize_os_distribution()
    
    # Save results if necessary
    vm_data.save_to_csv("output.csv")

if __name__ == "__main__":
    main()
