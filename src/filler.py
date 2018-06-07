#!/usr/bin/python3

from snmp import *
import elasticsearch as es
import mappings
from credentials import *
import time
import datetime
import logging
import config as cnf

config = cnf.config
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
  index_name = esc["index_name"] +\
              "-"+str(datetime.datetime.utcnow().strftime("%Y-%m"))
  ips = config["ips"]
  oids = config["oids"]
  url = esc["protocol"]+"://"+esc["hostname"]+':'+esc["port"]+"/"+index_name
except KeyError as e:
  cnf.error(e.args[0])

es.put_mapping(url, mappings.snmp_throughput, auth=(user, pwd))

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
        es.post(url+"/snmp/", auth=(user, pwd), json=obj)
      except EsUnknownErrorException:
        logging.error("Unknown exception encountered while try to communicate with elasticsearch.")

logging.info("Job done, exiting with 0")
