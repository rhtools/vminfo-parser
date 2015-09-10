import socket
import os
import subprocess
import sys

from helper_functions import ErrorHelper, FindFiles

NO_SSL_CHECK = False
python_version = sys.version.split()[0]

try:
    from M2Crypto import SSL
except ImportError:
    try:
        import yum
        yum_base = yum.YumBase()
        searchlist = ['name']
        package_to_install = ['m2crypto']
        matches = yum_base.searchGenerator(searchlist, package_to_install)
        for (package, matched_value) in matches:
            if package.name == package_to_install[0]:
                yum_base.install(package)
                yum_base.buildTransaction()
                yum_base.processTransaction()
    except:
        print("Error importing SSL.")
        NO_SSL_CHECK = True
import datetime

hostname = socket.gethostname()
GENERIC_BINARY_LOCATION = "/usr/local"
JAVA_BINARY_LOCATION = "/usr/java"


class GenericServerType(object):

    """ This class is intended to have its __init__ variables overwritten through inheritance
    The get_version_from_manifest function should populate a list of versions from Autodata applications
    """

    location_to_search = "/usr/local"
    file_type = "*.war"

    def __init__(self):
        component_list = FindFiles.find_files(self.location_to_search, self.file_type)
        self.found_manifest_version = []
        self.get_version_from_manifest(component_list)
        self.java_version_list = JavaVersion()

    def get_version_from_manifest(self, component_list):
        for autodata_component in component_list:
            if "backups" not in autodata_component and "purged" not in autodata_component.lower():
                check_manifest_command = "unzip -p %s META-INF/MANIFEST.MF" % autodata_component
                check_warfile = ErrorHelper.identify_problem(check_manifest_command,
                                                             autodata_component)
                for line in check_warfile.split("\n"):
                    # The manifest file should have a line that starts with the word "version"
                    # so look for case-insensitive
                    if line.lower().startswith("version") or line.startswith("Implementation-Version"):
                        component_with_path_removed = autodata_component.split("/")[-1] + ": \t" + line.split()[1]
                        if component_with_path_removed in self.found_manifest_version:
                            pass
                        else:
                            self.found_manifest_version.append(component_with_path_removed)


class ETLServer(GenericServerType):

    if "xet" in hostname:
        location_to_search = "/usr/local/etl"
    file_type = "*dependencies.jar"


class WarfileServer(GenericServerType):

    file_type = "*.war"


class AnnouncementServer(GenericServerType):

    location_to_search = "/usr/local/etl"
    file_type = "*.war"

    def __init__(self):
        component_list = FindFiles.find_files(self.location_to_search, self.file_type)
        self.found_manifest_version = []
        self.get_version_from_manifest(component_list)
        self.file_type = "*.jar"
        self.get_version_from_manifest(component_list)


class JavaVersion:

    def __init__(self):
        self.java_version_list = []
        self.get_java_version()

    def get_java_version(self):
        for java_version in FindFiles.find_files(JAVA_BINARY_LOCATION, "java"):
            if os.path.islink(os.path.basename(java_version)):
                pass
            else:
                if "gcj" in java_version or "gij" in java_version:
                    found_java_version = subprocess.Popen([java_version, '--version'],
                                                          stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                                          stderr=subprocess.PIPE).stdout.read().split()[2]
                else:
                    found_java_version = subprocess.Popen([java_version, '-version'],
                                                          stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                                          stderr=subprocess.PIPE).stderr.read().split()[2]
                append_me = java_version + ": " + found_java_version
                self.java_version_list.append(append_me)
        self.java_version_list.append(" ,")
        return(self.java_version_list)


class DatabaseVersionInformation:

    def find_mysql(self):
        mysqld_location = "/usr/sbin/mysqld"
        mysql_command = mysqld_location + " --version"
        found_mysql_version = ErrorHelper.identify_problem(mysql_command, "MySQL").split()[2].strip(",")
        return(found_mysql_version)

    def find_mongodb(self, mongo_server=None):
        mongo_dir = "/usr/local/mongodb/bin"
        # The vis servers do not seem to follow a standard for mongo paths so we have to hack around it
        # I am hoping that there is only one version of mongo installed on the vis server or this will break
        if mongo_server == "vis_mongodb_server":
            mongo_dir = "/usr/local/mongodb"
        mongo_binary = "mongo"
        mongo_command = mongo_dir + os.sep + mongo_binary + " --version"
        found_mongo_version = ErrorHelper.identify_problem(mongo_command, "MongoDB").split()[3].strip(",")
        return(found_mongo_version)


class WebStackInformation:

    """ This class will handle getting versions for tomcat, log4j, java, apache, openssl, portfoliomanager and creditapp warfiles
     Unfortunately since we do not have a unified location for verion numbers, there will be a new function for each client
     And possibly each warfile depending on where the version number can be read from. """

    def __init__(self):
        self.all_tomcat_versions = []
        tomcat_version_script = "version.sh"
        self.log4j_version_list = []
        self.get_tomcat_version(tomcat_version_script)
        if not NO_SSL_CHECK:
            self.get_ssl_information((socket.gethostname()))
        self.get_apache_version()
        self.get_openssl_version()

    def get_apache_version(self):
        httpd_path = "/usr/sbin/httpd"
        version_command = httpd_path + " -v"
        self.apache_version = ErrorHelper.identify_problem(version_command, "Apache").split()[2].split("/")[1].rstrip()

    def get_tomcat_version(self, tomcat_version_script):
        for tomcat_instance in FindFiles.find_files(GENERIC_BINARY_LOCATION, tomcat_version_script):
            version_script = ErrorHelper.identify_problem(tomcat_instance, "tomcat")
            found_tomcat_version = version_script.split()[27]
            tomcat_location = version_script.split()[2].split("/")[-1]
            addme = tomcat_location + ": " + found_tomcat_version + "; "
            self.all_tomcat_versions.append(addme)
        self.all_tomcat_versions.append(",")

    def get_openssl_version(self):
        openssl_path = "/usr/bin/openssl"
        ssl_command = "%s version" % openssl_path
        self.ssl_version = ErrorHelper.identify_problem(ssl_command, "OpenSSL").split()[1]

    def get_ssl_information(self, hostname):

        ssl_context = SSL.Context()
        # I am enabling unknown CA's to deal with self-signed certs
        ssl_context.set_allow_unknown_ca(True)
        ssl_context.set_verify(SSL.verify_none, 1)
        connect_to_server_over_https = SSL.Connection(ssl_context)
        connect_to_server_over_https.postConnectionCheck = None
        timeout = SSL.timeout(15)
        connect_to_server_over_https.set_socket_read_timeout(timeout)
        connect_to_server_over_https.set_socket_write_timeout(timeout)
        try:
            connect_to_server_over_https.connect((hostname, 443))
        except Exception, err:
            print("%s: %s" % (hostname, err))
            self.cert_expiration_date = "Error getting Expiration date"
            return

        cert = connect_to_server_over_https.get_peer_cert()

        try:
            self.cert_expiration_date = str(cert.get_not_after())
            if "2.4" in python_version:
                import time
                cert_as_datetime_object = time.strptime(self.cert_expiration_date, "%b %d %H:%M:%S %Y GMT")
                return
            else:
                cert_as_datetime_object = datetime.datetime.strptime(self.cert_expiration_date, "%b %d %H:%M:%S %Y GMT")
            todays_date = datetime.datetime.now()
            time_to_expiry = (cert_as_datetime_object - todays_date).days
            if time_to_expiry > 365:
                self.time_to_certificate_expiry = str(round((time_to_expiry / 365) , 2)) + " years"
            else:
                self.time_to_certificate_expiry = str(time_to_expiry) + " days"
        except AttributeError:
            self.cert_expiration_date = "Error getting Expiration date"
            pass
        connect_to_server_over_https.close
