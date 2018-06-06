#!/usr/bin/python3

snmp_throughput = {
  "mappings":{
    "snmp": {
      "properties": {
        "date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss||epoch_millis||epoch_second"
        },
        "ip": {
          "type": "ip"
        },
        "direction":{
          "type": "keyword"
        },
        "values": {
          "type": "long"
        }
      }
    }
  }
}
