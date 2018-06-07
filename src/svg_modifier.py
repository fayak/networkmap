#!/usr/bin/python3

import os
from bs4 import BeautifulSoup as Soup

colors = {"white": "#ffffff","green": "#00ff00","grey":"#555555","orange":"#ffa500"}


try:
  svg_file = open("resources/kb.svg", "r")
  xml = svg_file.read()
  svg_file.close()
except FileNotFoundError:
  exit(1)
soup = Soup(xml, "xml")
el = soup.findAll("ellipse", {"id":"sw-cri-3IE-status"})[0]
style = dict(item.split(":") for item in el["style"].split(";"))

color = style["fill"]
style["fill"] = colors["green"]
el["style"] = ";".join(['%s:%s' % (key, value) for (key, value) in style.items()])
print(soup.prettify(formatter='xml'))

new_svg = open("resources/kb_modified.svg", "w")

new_svg.write(str(soup))
