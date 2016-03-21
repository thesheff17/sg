#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Dan Sheffner Dan@Sheffner.com
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
This script will setup a centos or ubuntu machine to use python-pip
and virtualenv
"""

# python imports
import __main__ as main
import logging
import sys
import subprocess
import os
import shutil

# automatically detect file name being called
fileName = main.__file__
fileName = fileName.replace("./", "")
fileName = fileName.replace(".py", "")
fileName = fileName + ".log"

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
while len(logger.handlers) > 0:
    del logger.handlers[0]
ch = logging.FileHandler(fileName)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s \
                              - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)


class Linux(object):
    """
    This class will configure your linux distro into a python virtual env
    """

    version = '0.1'

    def __init__(self):
        self.home_dir = os.path.expanduser("~")

        # outside the virtualenv
        self.pip_packages = 'awscli awsebcli virtualenv boto3'

        # inside the virtualenv
        self.virt_pip_packages = 'django'

    def run_command(self, command, use_shell=False, working_dir=None):
        """
        Runs the linux command and exits if it fails

        :type command: string
        :param command: the command list you want to run

        :type use_shell: bool
        :param use_shell: should the subprocess call use a shell
        """

        # runs the command and gets the status
        if use_shell:
            status = subprocess.call(command, shell=use_shell, cwd=working_dir)
        else:
            command_list = command.split()
            status = subprocess.call(command_list, shell=use_shell,
                                     cwd=working_dir)

        if status != 0:
            logger.error("Failed Command: " + command)
            sys.exit()
        else:
            logger.info("Successful Command: " + command)

    @staticmethod
    def check_root():
        """
        Figures out if the user is root or not while running these scripts
        """
        userId = os.getuid()
        if userId is not 0:
            message1 = "This script requires root privileges.  exiting..."
            print message1
            logger.error(message1)
            sys.exit()

    @staticmethod
    def distro_check():
        """
        checks which linux distro you are on
        """
        linux_distro = ''
        if os.path.isfile('/etc/redhat-release'):
            linux_distro = 'centos'

        if os.path.isfile('/etc/lsb-release'):
            linux_distro = 'ubuntu'

        if linux_distro == '':
            message1 = 'sorry unable to detect which linux distro you are ' + \
                'running.  Exiting...'
            logging.error(message1)
            print message1
            sys.exit()

        return linux_distro

    def distro_setup(self):
        """
        installs the packages you need to use python2.7 and python pip
        """
        distro = self.distro_check()
        if distro == 'ubuntu':
            commands1 = ['apt-get update', 'apt-get upgrade -y', 'apt-get ' +
                         '-y install python-pip build-essential git-core']

            for each in commands1:
                self.run_command(each)

        if distro == 'centos':
            commands2 = ['rpm -iUvh  http://dl.fedoraproject.org/pub/epel' +
                         '/7/x86_64/e/epel-release-7-5.noarch.rpm',
                         'yum -y update', 'yum -y install python-pip git',
                         'useradd -m centos']
            for each in commands2:
                self.run_command(each)

        # upgrade pip to the lastest
        self.run_command('pip install --upgrade pip')

    def pip_setup(self):
        """
        configures the virtualenv for you
        """
        distro = self.distro_check()
        commands1 = ['pip install ' + self.pip_packages, 'mkdir /home/'
                     + distro + '/.virtualenvs', 'virtualenv /home/' + distro +
                     '/.virtualenvs/sg']

        for each in commands1:
            print each
            self.run_command(each)

        # install pip packages
        self.run_command('/bin/bash -c "source /home/' + distro +
                         '/.virtualenvs/sg/bin/activate && pip install ' +
                         self.virt_pip_packages + '"', use_shell=True)

    def configure_awsfile(self):
        """
        configures aws files
        """
        distro = linux.distro_check()

        os.mkdir('/home/' + distro + '/.aws/')

        self.run_command('clear')
        key = raw_input("What is your aws access key id?\n")
        secret_key = raw_input("What is your aws secret key?\n")
        message1 = 'What region do you want to use? Use us-east-1 if you ' + \
                   'do not know.\n'
        region = raw_input(message1)

        with open("/home/" + distro + '/.aws/config', 'w') as file1:
            file1.write('[profile eb-cli]\n')
            file1.write('aws_access_key_id = ' + key + '\n')
            file1.write('aws_secret_access_key = ' + secret_key + '\n')
            file1.write('[default]\n')
            file1.write('region = ' + region)

        with open("/home/" + distro + '/.boto', 'w') as file2:
            file2.write('[Credentials]\n')
            file2.write('aws_access_key_id = ' + key + '\n')
            file2.write('aws_secret_access_key = ' + secret_key + '\n')

    def copy_non_privileged(self):
        distro = linux.distro_check()
        shutil.copyfile('/root/sg.py', '/home/' + distro + '/sg.py')
        shutil.copyfile('/root/linux.py', '/home/' + distro + '/linux.py')

    def fix_permissions(self):
        """
        fix the permissions of the centos or ubuntu user
        """
        distro = self.distro_check()
        self.run_command('chown -R ' + distro + ':' + distro + ' /home/' +
                         distro + '/')

if __name__ == '__main__':
    print 'linux.py started...'

    linux = Linux()
    linux.check_root()
    linux.distro_setup()
    linux.pip_setup()
    linux.configure_awsfile()
    linux.copy_non_privileged()
    linux.fix_permissions()

    print 'linux.py completed.'
