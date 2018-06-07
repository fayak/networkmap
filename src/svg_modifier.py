#!/usr/bin/python3

import os
from bs4 import BeautifulSoup as Soup
import config as cnf
import logging
from snmp import *
config = cnf.config
colors = {"white": "#ffffff","green": "#00ff00","grey":"#555555","orange":"#ffa500"}

def poll_status(ip, oid):
  logging.info("Scanning "+ip)
  values = snmpGet(oid, ip)
  ret = []
  if not values:
      logging.warning(ip + " is unreachable or there's no SNMP server running")
      return None
  else:
    for val in values:
      ret.append(int(values[val]))
  return ret

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
  url_base = esc["protocol"]+"://"+esc["hostname"]+':'+esc["port"]+"/"
  user = esc["user"]
  pwd = esc["password"]
  cooldown = config["time_between_scans"]
  oids_status = config["oids_status"]
except KeyError as e:
  cnf.error(e.args[0])



try:
  svg_file = open("resources/kb.svg", "r")
  xml = svg_file.read()
  svg_file.close()
except FileNotFoundError:
  exit(1)
soup = Soup(xml, "xml")

def change_svg_color(key, color, form):
  global soup
  global colors
  el = soup.find(form, {"id":key})
  try:
    style = dict(item.split(":") for item in el["style"].split(";"))
  except TypeError:
    return False
  style["fill"] = colors[color]
  el["style"] = ";".join(['%s:%s' % (key, value) for (key, value) in style.items()])
  return True

def change_switch_status(switch, color):
  change_svg_color(switch+"-status", color, "ellipse")

def change_switch_port(key, color):
  change_svg_color(key, color, "rect")


switch = "sw-cri-lab"
change_switch_status(switch, "green")
for domain in ips:
  i = 1
  for status in poll_status(ips[domain], oids_status[0]): #FIXME
    logging.info("status:" + str(status))
    if status == 1:
      change_switch_port(domain+"-"+str(i), "green")
    else:
      change_switch_port(domain+"-"+str(i), "grey")
    i += 1

new_svg = open("resources/kb_modified.svg", "w")
new_svg.write(str(soup))
