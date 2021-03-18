
from configparser import ConfigParser
from flask import current_app
import os

class MessageQueue(object):
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    configfile = os.path.join(basedir,'queue.cfg')

    # def __init__(self):
    #     if not os.path.exists(self.configfile):



    def get_queue(self):
        with open(self.configfile, 'r') as f:
            lines = f.readlines()
            return lines

    def add_queue(self,value):
        mg = '{0}\n'.format(value)
        with open(self.configfile, 'a') as f:
            f.write(mg)

    def clean_queue(self):
        with open(self.configfile, 'w') as fr:
            fr.write('')

