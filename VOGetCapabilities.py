"""
This file is part of VOGetCapabilities
12/09/2016
Author : Chiara Marmo (chiara.marmo@u-psud.fr)
Copyright : CNRS, Universite Paris-Sud
"""

import re
from lxml import etree as ElementTree
from astropy.io import votable
from astropy.io.votable.tree import VOTableFile, Resource, Table, Param, Field


votable = VOTableFile()

parser = ElementTree.XMLParser(recover=True)
f = open('WMSgetcapabilities.xml','r')
string = f.read()
root = ElementTree.fromstring(string, parser)
for element in root:
  res = element.tag
  if (res!=ElementTree.Comment):
    resid=re.sub(':','_',res)
    resource = Resource(name=res,ID=resid)
    votable.resources.append(resource)
    #print res
    table = Table(votable)
    resource.tables.append(table)
    for param in element:
      par = param.tag
      value = param.text
      #print par
      if value is None:
        listvalue=param.items()
        value=listvalue
      dt=type(value).__name__
      if (dt=="str"):
        dt="char"
        arraysize="*"
        table.params.extend([
          Param(votable, name=par, datatype=dt, value=value)])
      elif (dt=="list"):
        if (len(value)>0):
          for tup in value:
            #print tup[0]
            table.params.extend([
              Param(votable, name=tup[0], datatype="char", value=tup[1])])

votable.to_xml("VOWMSgetcapabilities.xml")
