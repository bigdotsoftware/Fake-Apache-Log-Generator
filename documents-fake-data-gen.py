#!/usr/bin/python
import time
import datetime
import pytz
import numpy
import random
import gzip
import zipfile
import sys
import argparse
from faker import Faker
from random import randrange
from tzlocal import get_localzone
local = get_localzone()

#todo:
# allow writing different patterns (Common Log, Apache Error log etc)
# log rotation


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

parser = argparse.ArgumentParser(__file__, description="Fake Apache Log Generator")
parser.add_argument("--output", "-o", dest='output_type', help="Write to a Log file, a gzip file or to STDOUT", choices=['LOG','GZ','CONSOLE'] )
parser.add_argument("--log-format", "-l", dest='log_format', help="Log format, Common or Extended Log Format ", choices=['CLF','ELF'], default="ELF" )
parser.add_argument("--num", "-n", dest='num_lines', help="Number of lines to generate (0 for infinite)", type=int, default=1)
parser.add_argument("--prefix", "-p", dest='file_prefix', help="Prefix the output file name", type=str)
parser.add_argument("--sleep", "-s", help="Sleep this long between lines (in seconds)", default=0.0, type=float)

args = parser.parse_args()

log_lines = args.num_lines
file_prefix = args.file_prefix
output_type = args.output_type
log_format = args.log_format

faker = Faker()

timestr = time.strftime("%Y%m%d-%H%M%S")
otime = datetime.datetime.now()

outFileName = 'documents_data_'+timestr+'.log' if not file_prefix else file_prefix+'_access_log_'+timestr+'.log'

for case in switch(output_type):
    if case('LOG'):
        f = open(outFileName,'w')
        break
    if case('GZ'):
        f = gzip.open(outFileName+'.gz','w')
        break
    if case('CONSOLE'): pass
    if case():
        f = sys.stdout

flag = True
while (flag):
    if args.sleep:
        increment = datetime.timedelta(seconds=args.sleep)
    else:
        #increment = datetime.timedelta(seconds=random.randint(30, 300))
        increment = datetime.timedelta(milliseconds=random.randint(0, 300))
        #increment = datetime.timedelta(seconds=random.randint(0, 5))
    otime += increment

    ip = faker.ipv4()
    dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
    tz = datetime.datetime.now(local).strftime('%z')
    content = faker.text()
    #https://faker.readthedocs.io/en/master/locales/la.html?highlight=#faker.providers.lorem.la.Provider.text

    f.write('%s - - [%s %s] "%s"\n' % (ip,dt,tz,content))
    f.flush()

    log_lines = log_lines - 1
    flag = False if log_lines == 0 else True
    if args.sleep:
        time.sleep(args.sleep)
