=================================================
Sg - Auto config django app for elastic beanstalk
=================================================

Created By Dan Sheffner
-----------------------

prerequisites
~~~~~~~~~~~~~

Log into the aws dashboard https://aws.amazon.com/console/ and go to service
AWS Identity and Access Management (IAM). You will need the private and public
key amazon gives you for this service.

****************
Ubuntu 14.04 LTS
****************

Run as root user

::

    $ apt-get update
    $ apt-get install -y python curl
    $ cd /root/
    $ curl -O https://raw.githubusercontent.com/thesheff17/sg/master/linux.py
    $ curl -O https://raw.githubusercontent.com/thesheff17/sg/master/sg.py
    $ python linux.py

Run as ubuntu user

::

    $ cd /home/ubuntu/
    $ python sg.py

********
Centos 7
********

Run as root user

::

    $ cd /root/
    $ curl -O https://raw.githubusercontent.com/thesheff17/sg/master/linux.py
    $ curl -O https://raw.githubusercontent.com/thesheff17/sg/master/sg.py
    $ python linux.py

Run as centos user

::

    $ cd /home/centos/
    $ python sg.py


*********
More info
*********

linux.py - is a wrapper around ubuntu and centos distro and configures python,
virtualenv, pip packages, django, and files for aws. Requires root access.

sg.py - runs under a non privileged user (centos/ubuntu) and creates a
django project, migrates the db, and deploys it to an elastic beanstalk env.
It also queries the elastic load balancer at the end and sends it to the console.

***********
Example URL
***********
`http://awseb-e-p-awsebloa-eg6641tlb1to-630042528.us-east-1.elb.amazonaws.com/`

lxc ubuntu container testing:

::

   $ lxc-stop -n ubuntu1 && lxc-destroy -n ubuntu1 && lxc-create -n ubuntu1 -t \
   download -- --dist ubuntu --release trusty --arch amd64 && lxc-start -d -n \
   ubuntu1 && cp sg.py linux.py /var/lib/lxc/ubuntu1/rootfs/root/ && lxc-attach \
   -n ubuntu1

lxc centos container testing:

::

   $ lxc-stop -n centos1 && lxc-destroy -n centos1 && lxc-create -n centos1 -t \
   centos -- --release 7 && lxc-start -d -n centos1 && cp linux.py sg.py \
   /var/lib/lxc/centos1/rootfs/root/ && lxc-attach -n centos1 
