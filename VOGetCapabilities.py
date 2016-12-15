"""
This file is part of VOGetCapabilities
15/12/2016
Author : Chiara Marmo (chiara.marmo@u-psud.fr)
Copyright : CNRS, Universite Paris-Sud
"""

import re
import numpy as np
from lxml import etree as ElementTree
from astropy.io import votable
from astropy.io.votable.tree import VOTableFile, Resource, Table, Param, Field
import codecs

votable = VOTableFile()

parser = ElementTree.XMLParser(recover=True)
f = codecs.open('WMSgetcapabilities.xml','r','utf-8')
string = f.read()
root = ElementTree.fromstring(string, parser)
for element in root:
  res = element.tag
  if (res!=ElementTree.Comment):
    resid=re.sub(':','_',res)
    resource = Resource(name=res,ID=resid)
    votable.resources.append(resource)
    table = Table(votable)
    resource.tables.append(table)
    for param in element:
      par = param.tag
      value = param.text
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
            table.params.extend([
              Param(votable, name=tup[0], datatype="char", value=tup[1])])
      if (par=="Layer"):
        lresource = Resource(name=par,ID=par)
        votable.resources.append(lresource)
        j = 0
        data = []
        for layer in param:
          lay = layer.tag
          #print lay
          datalay = []
          if (lay=="Layer"):
            for field in layer:
              if (j==0):
                table.fields.extend([
                  Field(votable, name=field.tag, datatype="char", arraysize="*")])
              if field.text == None:
                field.text = "None"
              datalay.append(field.text)
              try:
                i = i + 1
                table.create_arrays(i)
              except:
                i = 0
            j = 1
          if datalay != []:
            data.append(datalay)
            #tdata = zip(*data)
        try:
          table.array = (np.ma.asarray(data,dtype='str'))
          table.array.mask = True
        except:
          i = 0
          #mask = np.ones(len(data))

votable.to_xml("VOWMSgetcapabilities.xml")
