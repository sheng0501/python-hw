#!/usr/bin/python

# program assumes you have enough access to the remote server and uses openSSH config in your
# .ssh directory

import paramiko
import argparse
import os
import sys


parser = argparse.ArgumentParser(description='simple user listing tool')
parser.add_argument('-H, --host', help='remote host',
                    required=True, dest='host')

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


sftp = client.open_sftp()
results = sftp.open('/etc/passwd')
print('{:<32s}{:<8s}{:<s}'.format('username', 'uid', 'comment'))
l = results.readline()
while l:
    l = l.strip()
    fields = l.split(':')
    print('{:<32s}{:<8s}{:<s}'.format(fields[0], fields[2], fields[4]))
    l = results.readline()

sys.exit(0)
