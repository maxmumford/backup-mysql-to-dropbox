#!/usr/bin/python
import os
import datetime
import time
from optparse import OptionParser
import cli_client

# get command line arguments
parser = OptionParser()
parser.add_option("-d", "--databases", dest="databases", help="List of databases to backup")
parser.add_option("-u", "--username", dest="username", help="MySQL user name")
parser.add_option("-p", "--password", dest="password", help="MySQL password", default='')
parser.add_option("-k", "--app-key", dest="app_key", help="Dropbox App Key")
parser.add_option("-s", "--app-secret", dest="app_secret", help="Dropbox app secret")
(options, args) = parser.parse_args()

# process options
assert options.databases, 'You must specify a comma separated list of databases'
options.databases = ',' in options.databases and list(set([db for db in options.databases.split(',')])) or [options.databases]

# mysql backup function
def backup_mysql_database(username, password, databases_to_backup):
    if not hasattr(databases_to_backup, '__iter__'):
        databases_to_backup = [databases_to_backup]

    backup_names = []

    for database in databases_to_backup:
        backup_date = time.strftime('%Y%m%d%H%M%S')

        # takes backup in the same location as script
        cmd_backup = "mysqldump -u{0} {1} {2} > {2}_{3}.sql".format(username, password and '-p%s' % passsword or '', database, backup_date)

        # zips the backup just taken
        cmd_zip = "zip {0}_{1}.zip {0}_{1}.sql".format(database, backup_date)

        # deletes the .sql backup just taken
        cmd_remove_backup = "rm -f {0}_{1}.sql".format(database, backup_date)

        # execute commands
        os.system(cmd_backup)
        os.system(cmd_zip)
        os.system(cmd_remove_backup)

        # append database name to list
        backup_names.append("{0}_{1}.zip".format(database, backup_date))

    return backup_names

# take backup
backup_names = backup_mysql_database(options.username, options.password, options.databases)

# get connection to dropbox
term = cli_client.DropboxTerm(options.app_key, options.app_secret)

# prompt for authentication if not already authenticated
if 'token_store.txt' not in os.listdir('.'):
    term.do_login([])

# upload each backup taken
for backup in backup_names:
    term.do_put([backup, backup])
    os.remove(backup);
