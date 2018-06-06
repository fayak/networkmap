#!/usr/bin/python3

from snmp import *
import elasticsearch as es
import mappings
from credentials import *
import time
import datetime

index_name = "snmp-throughput-v1-"+str(datetime.datetime.utcnow().strftime("%Y-%m"))

ips = [
  "192.168.240.240",
#  "192.168.2.240"
]

oids = {
  "in":"1.3.6.1.2.1.31.1.1.1.6",
  "out":"1.3.6.1.2.1.31.1.1.1.10"
}

es.put_mapping(url+"/"+index_name, mappings.snmp_throughput, auth=(user, pwd))

for ip in ips:
  for oid in oids:
    obj = {}
    obj["ip"] = ip;
    obj["date"] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    obj["direction"] = str(oid)
    obj["values"] = []
    values = snmpGet(oids[oid], ip)
    for val in values:
      obj["values"].append(int(values[val]))
    print(obj)
    obj['values'] = 1
    es.post(url+"/"+index_name+"/snmp/", auth=(user, pwd), json=obj)

