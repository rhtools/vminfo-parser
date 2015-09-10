# Owner: Steve Ovens
# Date Created: Aug 2015
# Primary Function: This is a file intended to be supporting functions in various scripts such as the deploy_components
# and run_reports.py. This file will do nothing if run directly

import datetime
import os
import subprocess
import shutil
import socket
import fnmatch
import sys
import time


class ErrorHelper:

    """ This class runs most of the commands that require os.popen, it is used to trap any errors
     which occurs during the process of checking versions of various software"""

    @staticmethod
    def identify_problem(command, component):
        # Check to see if the binary for the command exists
        if "unzip" not in command:
            if os.path.isfile(command.split()[0]):
                command_results = os.popen(command).read()
            else:
                print("The script encountered problems determining the %s version on %s --" %
                      (component, socket.gethostname()))
                command_results = " "
        else:
            command_to_execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            command_results = command_to_execute.communicate()[0]
            exit_status = command_to_execute.returncode
            if exit_status > 0:
                command_results = " "
        return command_results


class FindFiles:

    """ the fnmatch module is required for this section after finding the file,
    os.path is used to create an absolute path to the files.
    The filenames are then returned as a generator"""

    @staticmethod
    def find_files(location_to_search, file_type):
        for root, dirs, files in os.walk(location_to_search):
            if "src" in dirs:
                dirs.remove('src')
            else:
                for basename in files:
                    if fnmatch.fnmatch(basename, file_type):
                        filename = os.path.join(root, basename)
                        yield filename


class ImportHelper:

    """ This class simply allows for the dynamic loading of modules which are not apart of the stdlib.
     It specifies which module cannot be imported and provides the proper pip install command as output to the user.
    """

    @staticmethod
    def import_error_handling(import_this_module, modulescope):
        try:
            exec("import %s " % import_this_module) in modulescope
        except ImportError:
            print("This program requires %s in order to run. Please run" % import_this_module)
            print("pip install %s" % import_this_module)
            print("To install the missing component")
            sys.exit()


class ValidConfigFile:

    """ This class is used to check the first line of a file for valid key words or sentences.
     It is a rudimentary check to ensure that the files being passed in as arguments are intended to be used with
     the program being run.
    """

    @staticmethod
    def config_check(config_file, valid_keyword):
        ImportHelper.import_error_handling("magic", globals())
        try:
            if "ASCII" in (magic.from_file(config_file)):
                is_this_my_config = open(config_file, 'r')
                first_line = is_this_my_config.readline()
                if valid_keyword in first_line:
                    print("\n%s header has valid key word, assuming this is a valid config" % config_file)
                    return(True)
                else:
                    print("This is a text file but does not appear to be a valid config file")
                    print("I am expecting to have an indication that this is a config file for %s" % valid_keyword)
                    print("In the first line")
                    sys.exit()
            # If the file isnt a text file, abort
            else:
                print("This does not appear to be a text file/valid config file...ABORT")
                sys.exit()
        except IOError:
            print("There was a problem opening " + config_file)
            sys.exit()

class CleanUp:

    @staticmethod
    def move_warfiles_to_backup_location(move_this_warfile, backup_location, warfile_version=None):
        todays_date = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d--%H_%M'))
        warfile_name = move_this_warfile.split("/")[-1]
        if warfile_version is not None:
            shutil.move(move_this_warfile, '%s/%s_%s_%s' % (backup_location, warfile_name, warfile_version,
                                                            todays_date))
        else:
            shutil.move(move_this_warfile, '%s/%s.%s' % (backup_location, warfile_name, todays_date))