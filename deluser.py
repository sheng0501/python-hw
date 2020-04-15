#!/usr/bin/python

# mainly passing info to useradd and add ssh key on top of that
# check https://linux.die.net/man/8/userdel for detail

# program assumes you have enough access to the remote server and uses openSSH config in your
# .ssh directory

import os
import paramiko
import argparse
import sys
import types

parser = argparse.ArgumentParser(description='simple user adding tool')

# Following are not in the userdel
parser.add_argument('username', metavar='username')
parser.add_argument('-H, --host', help='remote host',
                    required=True, dest='host')

# following are in
parser.add_argument('-f, --force', action='store_true',
                    help='This option forces the removal of the user account, even if the user is still logged in.', dest='-f')
parser.add_argument('-r, --remove', action='store_true',
                    help="Files in the user's home directory will be removed along with the home directory itself and the user's mail spool. Files located in other file systems will have to be searched for and deleted manually.", dest='-r')
parser.add_argument('-Z, --selinux-user', action='store_true',
                    help="Remove SELinux user assigned to the user's login from SELinux login mapping.", dest='-Z')

args = parser.parse_args()


# connection info
config = paramiko.SSHConfig()
config.parse(open(os.path.expanduser('~/.ssh/config')))
conf = config.lookup(args.host)
keyFile = conf['identityfile'][0]
k = paramiko.RSAKey.from_private_key(open(keyFile))

client = paramiko.SSHClient()
client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

client.connect(hostname=conf['hostname'], port=22,
               pkey=k, username=conf['user'])

userdelOptions = ' '.join([k+' '+v if type(v) is str else k for (k, v) in vars(args).items()
                           if v and not k in ['host', 'username']])

_, stdout, stderr = client.exec_command(
    'sudo /sbin/userdel ' + args.username + ' ' + userdelOptions)
exit_status = stdout.channel.recv_exit_status()
if exit_status != 0:
    print(stderr.read().decode('utf-8'))
    client.close()
    sys.exit(-1)

print('done')
client.close()
sys.exit(0)
