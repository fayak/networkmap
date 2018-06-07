#!/usr/bin/python3

from snmp import *
import elasticsearch as es
import mappings
import time
import datetime
import logging
import config as cnf
import sys
import signal
import threading

config = cnf.config
loop = True
current_date = ""

def scan(ips, oids, url, auth):
  for ip in ips:
    logging.info("Scanning "+ip)
    for oid in oids:
      logging.info("Fetching OID "+oid+"("+oids[oid]+")")
      obj = {}
      obj["ip"] = ip;
      obj["date"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
      obj["direction"] = str(oid)
      obj["values"] = []
      values = snmpGet(oids[oid], ip)
      if not values:
          logging.warning(ip + " is unreachable or there's no SNMP server running")
          break
      else:
        for val in values:
          obj["values"].append(int(values[val]))
        try:
          es.post(url+"/snmp/", auth=auth, json=obj)
        except EsUnknownErrorException:
          logging.error("Unknown exception encountered while try to communicate with elasticsearch.")

try:
  log_file = config["log_output_file"]
  log_level = getattr(logging, config["log_level"].upper(), None)
  if not isinstance(log_level, int):
    raise KeyError("log_level")
  if log_file:
    logging.basicConfig(format=config["log_output_format"],
                        filename=log_file,
                        level=log_level)
  else:
    logging.basicConfig(format=config["log_output_format"],
                        level=log_level)
    
  esc = config["elasticsearch"]
  index_name_raw = esc["index_name"]
  ips = config["ips"]
  oids = config["oids"]
  url_base = esc["protocol"]+"://"+esc["hostname"]+':'+esc["port"]+"/"
  user = esc["user"]
  pwd = esc["password"]
  cooldown = config["time_between_scans"]
except KeyError as e:
  cnf.error(e.args[0])



@cnf.static_var("exit", False)
def signal_handler(signal, frame):
  if signal_handler.exit:
    logging.warning("Exiting now")
    exit(0)
  logging.warning("Stopping required. Will stop gracefully within few seconds")
  logging.warning("Send a second SIGINT to close it now")
  signal_handler.i = True
  global loop
  loop = False
signal.signal(signal.SIGINT, signal_handler)

while loop:
  new_current_date = str(datetime.datetime.utcnow().strftime("%Y-%m"))
  if new_current_date != current_date:
    current_date = new_current_date
    index_name = index_name_raw +\
             "-"+str(datetime.datetime.utcnow().strftime("%Y-%m"))
    url = url_base + index_name
    logging.info("Putting mapping")
    es.put_mapping(url, mappings.snmp_throughput, auth=(user, pwd))

  logging.info("Beginning new scan")
  scan(ips, oids, url, (user, pwd))
  logging.info("Scan done")
  signal_handler.exit = True
  time.sleep(cooldown)
  signal_handler.exit = False

logging.info("Job done, exiting with 0")
