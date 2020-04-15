#!/usr/bin/python

# mainly passing info to useradd and add ssh key on top of that
# check https://linux.die.net/man/8/useradd for detail

# program assumes you have enough access to the remote server and uses openSSH config in your
# .ssh directory

import os
import paramiko
import argparse
import sys
import types

parser = argparse.ArgumentParser(description='simple user adding tool')

# Following are not in the useradd
parser.add_argument('username', metavar='username')
parser.add_argument('-H, --host', help='remote host',
                    required=True, dest='host')
parser.add_argument('-S, --ssh-public-key',
                    help="The key file location", dest="key")

# The following flags are in the useradd
parser.add_argument('-b, --base-dir', metavar='BASE_DIR',
                    help='The default base directory for the system if -d HOME_DIR is not specified.', dest='-b')
parser.add_argument('-c, --comment', metavar='COMMENT',
                    help='GECOS field of the new account', dest='-c')
parser.add_argument('-d, --home', metavar='HOME_DIR',
                    help="The new user will be created using HOME_DIR as the value for the user's login directory.", dest='-d')
parser.add_argument('-e, --expiredate', metavar='EXPIRE_DATE',
                    help='The date on which the user account will be disabled. The date is specified in the format YYYY-MM-DD.', dest='-e')
parser.add_argument('-f, --inactive', metavar='INACTIVE',
                    help='The number of days after a password expires until the account is permanently disabled.', dest='-f')
parser.add_argument('-g, --gid', metavar='GROUP',
                    help="The group name or number of the user's initial login group. The group name must exist. A group number must refer to an already existing group.", dest='-g')
parser.add_argument('-G, --groups', metavar='GROUP1[,GROUP2,...[,GROUPN]]]',
                    help='A list of supplementary groups which the user is also a member of.', dest='-G')
parser.add_argument('-k, --skel', metavar='SKEL_DIR',
                    help="The skeleton directory, which contains files and directories to be copied in the user's home directory, when the home directory is created by useradd.", dest='-k')
parser.add_argument('-K, --key', metavar='KEY=VALUE',
                    help='Overrides /etc/login.defs defaults (UID_MIN, UID_MAX, UMASK, PASS_MAX_DAYS and others). Multiple -K options can be specified, e.g.: -K UID_MIN=100 -K UID_MAX=499', dest='-K')
parser.add_argument('-l, --no-log-init',
                    help='Do not add the user to the lastlog and faillog databases.', action='store_true', dest='-l')
parser.add_argument('-m, --create-home', action='store_true',
                    help="Create the user's home directory if it does not exist.", dest='-m')
parser.add_argument(
    '-M', action='store_true', help="Do not create the user's home directory, even if the system wide setting from /etc/login.defs", dest='-M')
parser.add_argument('-N, --no-user-group', action='store_true',
                    help='Do not create a group with the same name as the user, but add the user to the group specified by the -g option or by the GROUP variable in /etc/default/useradd.', dest='-N')
parser.add_argument('-o, --non-unique', action='store_true',
                    help='Allow the creation of a user account with a duplicate (non-unique) UID.', dest='-o')
parser.add_argument('-p, --password', metavar='PASSWORD',
                    help='The encrypted password, as returned by crypt(3). The default is to disable the password.', dest='-r')
parser.add_argument('-r, --system', action='store_true',
                    help='Create a system account.', dest='-r')
parser.add_argument('-s, --shell', metavar='SHELL',
                    help="The name of the user's login shell.", dest='-s')
parser.add_argument('-u, --uid', metavar='UID',
                    help="The numerical value of the user's ID.", dest='-u')
parser.add_argument('-U, --user-group', action='store_true',
                    help="Create a group with the same name as the user, and add the user to this group.", dest='-U')
parser.add_argument('-Z, --selinux-user', metavar='SEUSER',
                    help="The SELinux user for the user's login. The default is to leave this field blank, which causes the system to select the default SELinux user.", dest='-Z')


args = parser.parse_args()
print(args.username)
print(' '.join(sys.argv[1:]))
print(sys.argv)

useraddOptions = ' '.join([k+' '+v if type(v) is str else k for (k, v) in vars(args).items()
                           if v and not k in ['host', 'username', 'key']])


config = paramiko.SSHConfig()
config.parse(open(os.path.expanduser('~/.ssh/config')))
conf = config.lookup(args.host)
print(conf)
keyFile = conf['identityfile'][0]
k = paramiko.RSAKey.from_private_key(open(keyFile))
# print(k)
client = paramiko.SSHClient()
client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
print(args.host)
client.connect(hostname=conf['hostname'], port=22,
               pkey=k, username=conf['user'])
stdin, stdout, stderr = client.exec_command(
    'sudo /usr/sbin/useradd ' + args.username + ' ' + useraddOptions)
exit_status = stdout.channel.recv_exit_status()
if exit_status != 0:
    print(stderr.read().decode('utf-8'))

client.close()
