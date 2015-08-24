#!/usr/bin/python
# this will run the reports on the remote server
# Apr 2013
# Updated June 7, 2015
# This script expects to be run with a single parameter: a list of hosts
# USAGE: run_reports.py -f test_list -e user@domain.com -u remoteactions -o /tmp
import os
import sys
import datetime
from optparse import OptionParser
import fileinput
from operator import itemgetter


todays_date = datetime.datetime.now().strftime("%Y-%m-%d")

parser = OptionParser()
parser.add_option('-e', dest='email_address', help='Email address to send report to')
parser.add_option('-f', dest='host_list', help='File containing list of hosts')
parser.add_option('-o', dest='output_location', help='Send report output here')
parser.add_option('-u', dest='ssh_username', help='The user to perform the remote actions as')
parser.add_option('--component-only-check', dest='component_only_check', help='Flag to only check component versions '
                                                                              '(i.e. jar/warfiles)')
(options, args) = parser.parse_args()

servers_with_no_components = ["my", "mongo", "xmg", "arb"]
mail_subject = ""

if options.host_list is None:
    print("Host list was not passed in")
    parser.print_help()
    sys.exit()

if options.ssh_username is None:
    print("No ssh username was specified")
    parser.print_help()
    sys.exit()

if options.email_address is None:
    print("No email address was specified")
    parser.print_help()
    sys.exit()

if options.output_location is None:
    print("No output location for the report was specified")
    parser.print_help()
    sys.exit()

reports_against_these_hosts = options.host_list
if options.component_only_check is not None:
    output_filename = "%s/%s_%s.txt" % (options.output_location, reports_against_these_hosts.split("/")[-1], todays_date)
else:
    output_filename = "%s/%s_%s.csv" % (options.output_location, reports_against_these_hosts.split("/")[-1], todays_date)
error_file = "%s/%s_%s.err" % (options.output_location, reports_against_these_hosts.split("/")[-1], todays_date)
report_to_this_email = options.email_address
ssh_user = options.ssh_username


##############################Functions
# This function is used to examin the list of hosts in the host file
# and compare it against a list of hosts which it will extract from a 'completed' report
def which_hosts_are_missing():
    # Set a local list for processing
    host_list = []
    # Because we need the fqdn, but the report relies on the host's hostname (which does not include the fqdn)
    # The easiest way to compare the lists is to split off the domain and put those in a list for comparison
    for host in open(reports_against_these_hosts).readlines():
        host = host.split(".")[0].lower()
        if host.startswith("#"):
            pass
        else:
            if options.component_only_check is not None:
                if not any(postfix in host.strip() for postfix in servers_with_no_components):
                    host_list.append(host.rstrip())
            else:
                host_list.append(host.rstrip())
    # Set a local list for the hosts which have reported in
    report_list = []
    for x in open(output_filename).readlines():
        if options.component_only_check is not None:
            reported_host = x.split(":")[0].lower()
        else:
            reported_host = x.split(",")[0].lower()
        if ".org" in reported_host or ".com" in reported_host or ".net" in reported_host:
            try:
                reported_host = reported_host.split(".")[0]
            except:
                pass
        report_list.append(reported_host)
    # This compares the two lists and returns a list of hosts which are not in the report
    hosts_missing_from_report = list(set(host_list) - set(report_list))
    return hosts_missing_from_report


# This function is used to determine if this is a first run through (i.e. step on the old file)
# Or whether we have to re-run some of the reports in case some of the hosts fail to repond
def set_write_mode(Hlist, write_mode):
    sys.stdout = open(output_filename, write_mode)
    # This is the spreadsheet header
    if "w" in write_mode:
        if options.component_only_check is not None:
            print("Component only check was initiated \n")
        else:
            print("Server, Environment, Sys (GB), Data (GB), Local (GB), Cpu Type, Number of Cores, Total Ram (MB), \
                  Linux Version:, kernel version, Repository, apache version, tomcat version, openssl version, java, MySql,\
                  MongoDB, rpm hash, certificate expiration, Antivirus")
        run_reports(Hlist)
    # This section is a little bit complicated but in effect we are going to recreate a list of hosts
    # In order to re-run the reports only on those hosts
    if "a" in write_mode:
        amended_list = []
        for missing_report_host in Hlist:
            for extracted_fqdn in host_fqdn:
                if missing_report_host in extracted_fqdn:
                    print(extracted_fqdn)
                    # This section matches missing hostname with an fqdn
                    amended_list.append(extracted_fqdn)
        run_reports(amended_list)


# This function controls the actual remote calls to the physical clients
def run_reports(Hlist):
    remote_script_location = "/usr/local/ops/scripts/create_machine_report.py"
    for host in Hlist:
        if host.startswith("#"):
            pass
        else:
            if not any(postfix in host.strip() for postfix in servers_with_no_components):
                if host.strip():
                    return_host_report = [""]
                    if options.component_only_check is not None:
                        return_host_report = os.popen('ssh -t %s@%s "sudo %s --component-only-check yes"' %
                                                      (ssh_user, host.rstrip(), remote_script_location)).read(),
                    else:
                        return_host_report = os.popen('ssh -t %s@%s "sudo %s"' % (ssh_user, host.rstrip(),
                                                                                  remote_script_location)).read(),
                    if "command not found" in return_host_report[0]:
                        print "The script was not found on the remote host: %s. Aborting to prevent a loop" % host.rstrip()
                        sys.exit()
                    print return_host_report[0],
                    sys.stdout = open(output_filename, "a")

##############################End functions

# Store the FQDN in a list so we dont have to read the file all the time
host_fqdn = []
for host in open(reports_against_these_hosts).readlines():
    if host.strip():
        if options.component_only_check:
            # The component only check does not need to query the database servers as no components
            # should exist on those boxes
            if not any(postfix in host.strip().lower() for postfix in servers_with_no_components):
                host_fqdn.append(host)
        else:
            host_fqdn.append(host)
        host_fqdn.sort()

# Create the proper files by writing stdout to a file
old_stdout = sys.stdout
set_write_mode(host_fqdn, "w")
sys.stdout = old_stdout

# Check to see which hosts may be in the list of hosts but not in the report
missing_hosts = which_hosts_are_missing()

# This is the counter that will abort the script after so many retries
failed_to_check_in = 0

# Check to see if the missing_hosts list is empty. If it is, we assume that the reports have been generated correctly
if missing_hosts == []:
    print "no hosts were missed... Report complete"
    pass
# This section will loop until there are no more hosts left to check
else:
    while missing_hosts != []:
        sys.stdout = old_stdout
        print "These hosts are missing from the report %s" % missing_hosts
        print "attempting to rerun reports on the missing host"
        set_write_mode(missing_hosts, "a")
        missing_hosts = which_hosts_are_missing()
        failed_to_check_in += 1
        if failed_to_check_in == 3:
            print "These hosts failed to check in after 3 attempts: %s" % missing_hosts
            break
    print "no hosts were missed... Report complete"

for line in fileinput.input(output_filename, inplace=1):
    if "sessionid.tdb" not in line:
        sys.stdout.write(line)

# This is used to sort the list by the component instead of the server
# This has to be done right before emailing out
file_to_send = open(output_filename).readlines()
lines = [line.split() for line in file_to_send if line.strip()]
lines.sort(key=itemgetter(1))
sys.stdout = open(output_filename, 'w')
for line in lines:
    print(" ".join(line))
sys.stdout = old_stdout

if options.component_only_check is not None:
    mail_subject = "Component Only check for %s" % reports_against_these_hosts.split("/")[-1]
else:
    mail_subject = "Machine report for %s" % reports_against_these_hosts.split("/")[-1]

os.system("echo 'report generation complete' | mutt -a '%s' -s '%s' -- %s" % (output_filename, mail_subject,
                                                                              report_to_this_email))
