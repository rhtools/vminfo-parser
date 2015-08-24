#!/usr/bin/python
# Owner: Steve Ovens
# Date re-Created: Jan 2014
# Modified: June 4, 2015
# Primary Function:
# This script is going to go through the current server and return
# Versions of variable programs which may or may not have been installed via the package manager
# Because we deploy things via tar.gz's centralized tools such as CFEngine have a hard time
# Determining package versions
# This script runs with no parameters but it relies upon 'get_system_info.py', 'get_versions.py'
# and 'helper_functions.py'. It was split up to make the code more modular and easy to maintain

import socket
import sys
from get_system_info import HardwareInformation, LinuxInformation
from get_versions import DatabaseVersionInformation, WebStackInformation, JavaVersion, WarfileServer, ETLServer, AnnouncementServer
from optparse import OptionParser

parser = OptionParser()
parser.add_option('--component-only-check', dest='component_only_check', help='Flag to only check component versions (i.e. jar/warfiles)')
(options, args) = parser.parse_args()

python_version = sys.version.split()[0]
# the "any()" method was introduced in python 2.5. I am going to create it in the case of python 2.4
if "2.4" in python_version:
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False

hostname = socket.gethostname().lower()
environment = hostname.split("-")[1]
mysql_server_postfixes = ["my"]
mongo_server_postfixes = ["mongo", "xmg", "arb"]
web_server_postfixes = ["xwa", "xws", "was", "svc"]
etl_server_postfixes = ["xet", "etl"]
announcement_server_postfixes = ["xan"]



def print_statement():

    """
    This function sets blank variables that can be overridden depending on the
    object being passed into the function. It's purpose is to make printing
    less error prone

    # The file output needs to be:
    # hostname, environment, system_disk, data disk, usr/local disk, cpu type, # of cpus, ram, OS Version, Kernel,
    # repository, apache, tomcat, openssl, log4j, java, mysql, mongodb, rpm_hash, ssl_cert, antivius,
    """
    if not options.component_only_check:
        apache_version = ""
        tomcat_versions = ""
        ssl_version = ""
        java_versions = ""
        certificate_expiration = ""
        # These are being initialized blank and then may be overridden if a database exists
        mysql_version = ""
        mongo_version = ""

        if not any(postfix in hostname for postfix in mysql_server_postfixes) or not \
                   any(postfix in hostname for postfix in mongo_server_postfixes):
            java_versions = JavaVersion()

        if any(postfix in hostname for postfix in web_server_postfixes) or \
               any(postfix in hostname for postfix in announcement_server_postfixes):
            web_components = WebStackInformation()
            apache_version = web_components.apache_version
            tomcat_versions = web_components.all_tomcat_versions
            ssl_version = web_components.ssl_version
            certificate_expiration = web_components.cert_expiration_date

        if any(postfix in hostname for postfix in mysql_server_postfixes):
            database_info = DatabaseVersionInformation()
            mysql_version = str(database_info.find_mysql())

        if any(postfix in hostname for postfix in mongo_server_postfixes):
            database_info = DatabaseVersionInformation()
            mongo_version = str(database_info.find_mongodb())

        for variable in (hostname, environment, hardware_info.list_of_all_system_disks, hardware_info.cpu_name, hardware_info.number_of_cores,
            hardware_info.total_ram, linux_info.os_version, linux_info.kernel_version, linux_info.yum_repository,
            apache_version, tomcat_versions, ssl_version, java_versions.java_version_list, mysql_version, mongo_version,
            linux_info.hash_output, certificate_expiration, ""):
                if type(variable) == list:
                    for element in variable:
                        print(element),
                else:
                    print("%s, " % variable.strip()),
    else:
        if any(postfix in hostname for postfix in web_server_postfixes) or \
                any(postfix in hostname for postfix in announcement_server_postfixes):
            warfile_info = WarfileServer()
            for component in warfile_info.found_manifest_version:
                print("%s: %s" % (hostname, component.replace(":", " =")))
            # SET runs their ETLs from XWS boxes so we need to kick off the java/jarfile for XWS
            if "set" in hostname:
                jarfile_info = ETLServer()
                for component in jarfile_info.found_manifest_version:
                    print("%s: %s" % (hostname, component.replace(":", " =")))
        if any(postfix in hostname for postfix in etl_server_postfixes) or any(postfix in hostname for postfix in announcement_server_postfixes):
            jarfile_info = ETLServer()
            for component in jarfile_info.found_manifest_version:
                print("%s: %s" % (hostname, component.replace(":", " =")))

# By default, we want to gather both the linux information and the hardware info on all servers
linux_info = LinuxInformation()
hardware_info = HardwareInformation()

print_statement()
