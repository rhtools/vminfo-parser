import os
import platform
import sys
import rpm


class HardwareInformation:

    def __init__(self):
        self.list_of_all_system_disks = []
        self.get_cpu_info()
        self.get_disk_info()
        self.get_ram_info()

    def get_cpu_info(self):
        # This method is self explanitory, it extracts the number of cpu cores and processor type
        # From /proc/cpuinfo
        self.number_of_cores = 0
        for cpu_info in os.popen("cat /proc/cpuinfo").read().split("\n"):
            if "model name" in cpu_info:
                self.cpu_name = cpu_info.split(": ")[1]
                self.cpu_name = self.cpu_name.strip()
            elif "processor" in cpu_info:
                self.number_of_cores += 1
        self.number_of_cores = str(self.number_of_cores)

    def get_disk_info(self):
        for line in open("/etc/mtab").readlines():
            if line.startswith("/dev"):
                if "boot" in line:
                    pass
                else:
                    partition = line.split()[1]
                    append_partition = self.disk_usage(partition)
                    self.list_of_all_system_disks.append(append_partition)
        # This if statement is used to make sure that the proper partition goes under the correct
        # heading in the csv file. At the time of writing I am expecting '/, /DATA, /usr/local'
        if not [value for value in self.list_of_all_system_disks if "DATA" in value.upper()]:
            self.list_of_all_system_disks.insert(1, "/DATA: Not Found,")
        if not [value for value in self.list_of_all_system_disks if "local" in value]:
            self.list_of_all_system_disks.insert(2, "/usr/local: Not Found, ")
        self.list_of_all_system_disks.sort()

    def disk_usage(self, path):
        disk_statistics = os.statvfs(path)
        free_disk_space = (disk_statistics.f_bavail * disk_statistics.f_frsize) / 1024 / 1024 / 1024.0
        total_space_available = (disk_statistics.f_blocks * disk_statistics.f_frsize) / 1024 / 1024 / 1024.0
        used_disk_space = ((disk_statistics.f_blocks - disk_statistics.f_bfree) * disk_statistics.f_frsize) / 1024 / 1024 / 1024.0
        # This rounds the numbers to 1 decimal point
        free_disk_space = "%.1f" % free_disk_space
        total_space_available = "%.1f" % total_space_available
        used_disk_space = "%.1f" % used_disk_space
        return "%s:  Total: %s      Free: %s      Used: %s," % (path, total_space_available, free_disk_space, used_disk_space)

    def get_ram_info(self):
        for mem_info in os.popen("cat /proc/meminfo").read().split("\n"):
            if "MemTotal" in mem_info:
                # meminfo displays ram in kB, like so: MemTotal:      3914516 kB
                # This strips out all but the digits and then converts it to MB
                self.total_ram = str(int(mem_info.split(": ")[1].replace(" kB", "").strip()) / 1024)
                # self.total_ram = str(self.total_ram)


class LinuxInformation:

    """ Get the current os release. Normally you could use platform.linux_distribution() but RedHat 5.xx
     does not have this method. Alternatively platform.dist() could be used, but it reports RHEL
     even if on CentOS. The only reliable method for RHEL 5.xx based OS is to use the /etc/redhat-release """

    def __init__(self):
        # This may be /etc/redhat-release, /etc/lsb-release or some other variant which may need to be changed
        release_file = "/etc/redhat-release"
        self.os_version = open(release_file).read().rstrip().lower()
        if "centos" in self.os_version:
            self.os_version = "CentOS " + self.os_version.split()[2]
        elif "red hat" in self.os_version:
            self.os_version = "RHEL " + self.os_version.split()[6]
        self.kernel_version = platform.release()
        self.get_installed_rpms()
        self.yum_repository = "Not available"
        try:
            yum_file = '/etc/yum.repos.d/CentOS-Base.repo'
            if os.path.isfile(yum_file):
                self.find_yum_repository(yum_file)
        except IOError:
            self.yum_repository = "Not available"

    def get_installed_rpms(self):
        rpm_list = []
        # log the rpms
        list_of_rpms = "rpm.lst"
        # This toggles the stdout to a file
        old_stdout = sys.stdout
        sys.stdout = open(list_of_rpms, "w")
        transActions = rpm.TransactionSet()
        all_rpms = transActions.dbMatch()
        # A list is not required to capture the output however, I want to produce an alphabetical sorting
        for individual_rpm in all_rpms:
            rpm_list.append("%s-%s-%s" % (individual_rpm['name'], individual_rpm['version'], individual_rpm['release']))
        # Sort the list alphabetically
        rpm_list.sort()
        # print the sorted list
        for rpms in rpm_list:
            print(rpms)
        sys.stdout = old_stdout
        try:
            import hashlib
            # Open the file for read-only and append the option to handle in case of being a binary file ('rb')
            file_to_hash = open(list_of_rpms, 'rb')
            sha_hash = hashlib.sha1()
        except ImportError:
            import sha
            sha_hash = sha.new()
            file_to_hash = open(list_of_rpms, 'rb')
        while True:
            # The data needs to be read in chunks for sha. SHA is more efficient than md5
            # because md5 can only handle 128 chunks
            data = file_to_hash.read(8192)
            # Loop through until there is no data left and then break the loop and calculate the final hash
            if not data:
                break
            sha_hash.update(data)
        self.hash_output = sha_hash.hexdigest()
        sys.stdout = old_stdout

    def find_yum_repository(self, yum_file):
        start = False
        for line in open(yum_file).readlines():
            # Every repo file will have a base, so scrape the repo from its baseurl
            if line.strip() == "[base]":
                start = True
            # By convention each repo file has a gpgcheck section, so stop reading the file there
            if line.strip().startswith("gpgcheck"):
                start = False
            if start:
                if "baseurl" in line:
                    self.yum_repository = line.split("centos/")[-1].split("/$releasever/")[0]
