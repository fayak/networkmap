#!/usr/bin/python3

from pysnmp.hlapi import *

se = SnmpEngine()

def snmpGet(oid, ip, community="public", port="161"):
  global se
  try:
    g = nextCmd(
        se,
        CommunityData(community),
        UdpTransportTarget((ip, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )
  except PySnmpError:
    return None
  ret = {}

  i = 1
  if g:
    for (eri, ers, erx, vars) in g:
      if not eri and not ers:
        try:
          for o,p in vars:
            ret[i] = int(p)
            i = i + 1
        except:
          return None
  if ret != {}:
    return ret
  return None

ips = [
  "192.168.240.240",
  "192.168.2.240"
]

oids = [
  "1.3.6.1.2.1.31.1.1.1.6",
  "1.3.6.1.2.1.31.1.1.1.10"
]

values = []

for ip in ips:
  ip_res = []
  for oid in oids:
    ip_res.append(snmpGet(oid, ip))
  values.append(ip_res)

print(values)
