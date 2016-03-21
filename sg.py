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
This script will create a local django env and deploy to amazon elastic
beanstalk
"""

# python imports
import __main__ as main
import logging
import re
import sys
import os
import time

# pip imports
import boto3

# custom imports
import linux
linux = linux.Linux()

# automatically log to file called
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


class Sg(object):
    """
    This class will configure a django app inside a virtualenv, and deploy it to
    an elastic beanstalk env.  Also it will attach an elastic load balancer
    (ELB)
    """

    version = '0.1'

    def __init__(self):
        self.home_dir = os.path.expanduser("~")

    @staticmethod
    def non_privileged_user():
        """
        Checks to see which user you are running this script as
        """
        userId = os.getuid()
        if userId is 0:
            message1 = 'You should run this script not as root. Usually ' + \
                'centos or ubuntu.'
            print message1
            logger.error(message1)
            sys.exit(1)

    def pick_name(self):
        """
        This method will pick a name for beanstalk and django app
        """
        linux.run_command('clear')
        message1 = 'What name would you like to use?  Only letters and ' + \
                   'numbers are avaliable. Should also be a minimum of ' + \
                   '4 characters due to some amazon constraints.\n'

        self.global_name = raw_input(message1)

        if not re.match("^[A-Za-z0-9]*$", self.global_name):
            message1 = 'Sorry you should not create a name with special ' + \
                       'characters.  Only letters and numbers are allowed'
            logging.error(message1)
            print message1
            sys.exit(1)

        if len(self.global_name) <= 4:
            message2 = 'sorry the name has to be a minimum of 4 characters.'
            logging.error(message2)
            sys.exit(1)

    def django_setup(self):
        """
        starts creating the layout for the django project
        """
        directory1 = self.home_dir + '/git'
        if not os.path.exists(directory1):
                os.makedirs(directory1)

        helper_command = '/bin/bash -c "source ' + self.home_dir + \
                         '/.virtualenvs/sg/bin/activate && '

        linux.run_command(helper_command + 'django-admin startproject ' +
                          self.global_name + '"', use_shell=True,
                          working_dir=self.home_dir + '/git/')

        linux.run_command(helper_command + 'pip freeze > requirements.txt"',
                          use_shell=True, working_dir=self.home_dir + '/git/' +
                          self.global_name)

        linux.run_command(helper_command + 'python manage.py migrate"',
                          use_shell=True, working_dir=self.home_dir + '/git/' +
                          self.global_name)

    def get_region(self):
        """
        pulls the region from the aws config file
        """
        file1 = self.home_dir + '/.aws/config'
        lines = [line.rstrip('\n') for line in open(file1)]
        for each in lines:
            if 'region' in each:
                line = each.split()
                region = line[2]
                logger.info('using region ' + region)

        return region

    def beanstalk_setup(self):
        """
        starts the process for creating the beanstalk env
        """
        region = self.get_region()
        directory2 = self.home_dir + '/git/' + self.global_name + \
            '/.ebextensions/'

        if not os.path.exists(directory2):
            os.makedirs(directory2)

        with open(directory2 + 'django.config', 'w') as file1:
            file1.write('option_settings:\n')
            file1.write('  aws:elasticbeanstalk:container:python:\n')
            file1.write('    WSGIPath: ' + self.global_name + '/wsgi.py\n')

        beanstalk_list = ['eb init -p python2.7 ' + self.global_name + ' -r ' +
                          region, 'eb init', 'eb create ' + self.global_name,
                          'eb deploy', 'eb status']

        for each in beanstalk_list:
            linux.run_command(each, working_dir=self.home_dir + '/git/' +
                              self.global_name + '/')

    def get_elb_name(self):
        """
        prints out the DNS name of the elastic load balancer attached to
        the elastic beanstalk env
        """
        print 'Sleeping 30 seconds...'
        time.sleep(30)
        elb_client = boto3.client('elb')
        ec2_client = boto3.client('ec2')

        # find the id of the instance with our tag
        filters = [{'Name': 'tag:Name', 'Values': [self.global_name]}]
        response = ec2_client.describe_tags(Filters=filters)
        id_to_search = response['Tags'][0]['ResourceId']

        # now loop through the ELB and find the DNS name
        response = elb_client.describe_load_balancers()
        for each in response['LoadBalancerDescriptions']:
            instances = each['Instances']
            dns = each['DNSName']
            for each2 in instances:
                instance_id = each2['InstanceId']
                if instance_id == id_to_search:
                    message1 = 'Your ELB is http://' + dns + '/ \n' + \
                        'Might take a couple min for the EC2 instance to ' + \
                        'become in service.'
                    print message1


if __name__ == '__main__':
    print 'sg.py started...'

    sg = Sg()
    sg.non_privileged_user()
    sg.pick_name()
    sg.django_setup()
    sg.beanstalk_setup()
    sg.get_elb_name()

    print 'sg.py finished.'
