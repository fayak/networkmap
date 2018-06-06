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
