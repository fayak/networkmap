#!/usr/bin/python3

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import time

default_index_settings = {"index": {"max_docvalue_fields_search" : 150 }}

#Not recommended, but we're having self signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class EsSecurityException(Exception):
  pass
class EsWrongMethodException(Exception):
  pass
class EsUnknownErrorException(Exception):
  pass

def es_comm(url, method="GET", auth=None, json=None):
  iteration = 1
  while True:
    try:
      if method == "GET":
        r = requests.get(url, auth=auth, json=json, verify=False)
      elif method == "POST":
        r = requests.post(url, auth=auth, json=json, verify=False)
      elif method == "PUT":
        r = requests.put(url, auth=auth, json=json, verify=False)
      else:
        raise EsWrongMethodException("Unhandled/Wrong HTTP method")
      break
    except requests.exceptions.RequestException as e:
      logging.warning("Unable to contact "+url+". Will try again in "+str(iteration * 30)+"s")
      time.sleep(iteration * 30)
      iteration *= 2
  rep = r.json()
  if "error" in rep:
    if "type" in rep["error"] and rep["error"]["type"] == "security_exception":
      raise EsSecurityException(str(rep["error"]))
    elif "type" in rep["error"] and rep["error"]["type"] == "resource_already_exists_exception":
      return rep
    else:
      raise EsUnknownErrorException(str(rep["error"]))
  else:
    return rep

def get(url, auth=None, json=None):
  return es_comm(url, "GET", auth, json)

def post(url, auth=None, json=None):
  return es_comm(url, "POST", auth, json)

def put_mapping(url, mapping, index_settings=None, auth=None, json=None):
  es_comm(url, "PUT", auth, mapping)
  if index_settings:
    es_comm(url + "/_settings", "PUT", auth, index_settings)
