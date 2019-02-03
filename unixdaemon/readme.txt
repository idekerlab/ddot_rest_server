The instructions in this readme provide steps
to install ddot_taskrunner.py as a service managed by systemd.
These instructions use the files in this directory and require
a centos 7 box with superuser access.

# Requirements

* ddotrunner user added to box and added to apache group
* apache user added to ddotrunner group
* ddotrunner added to docker group (to run docker images)


1) Create needed log directory

mkdir /var/log/ddot-taskrunner
chown ddotrunner.ddotrunner /var/log/ddot-taskrunner

2) Create conf file

Copy ddot-taskrunner.conf to /etc

3) Create systemd file

Copy ddot-taskrunner.service to /lib/systemd/system
cd /lib/systemd/system
chmod 777 ddot-taskrunner.service


4) Register script with systemd

systemctl daemon-reload
cd /lib/systemd/system
systemctl enable ddot-taskrunner
systemctl start ddot-taskrunner

5) Verify its running

ps -elf | grep ddot

# output
4 S ddotrun+ 15010     1  0  80   0 - 207903 poll_s 11:43 ?       00:00:02 /opt/miniconda3/bin/python /opt/miniconda3/bin/ddot_taskrunner.py --wait_time 1 --logconfig /etc/ddot-taskrunner.conf /var/www/ddot_rest/tasks




