#!/usr/bin/python3

import os
import logging
import json

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

def my_exit():
  logging.critical("Exiting ...")
  exit(1)
  
def error(key=None):
  if key:
    logging.critical("Config key not found: "+key)
  else:
    logging.critical("Invalid config file")
  my_exit()


if not os.path.isfile("config.json"):
  logging.critical("Config file ./config.json not found !")
  my_exit()

cnf_file = open("config.json", "r")
try:
  config = json.loads(cnf_file.read())
except:
  logging.critical("Invalid config file ./config.json !")
  my_exit()
