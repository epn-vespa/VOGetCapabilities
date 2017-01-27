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
import math

def VOGetCapabilities(filename,outfile):

  votable = VOTableFile()

  parser = ElementTree.XMLParser(recover=True)
  f = codecs.open(filename,'r','utf-8')
  string = f.read()
  string = bytes(bytearray(string, encoding='utf-8')) ## force utf-8 encoding even if xml says otherwise
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
          ltable = Table(votable)
          lresource.tables.append(ltable)
          j = 0
          data = []
          for layer in param:
            lay = layer.tag
            datalay = []
            if (lay=="Layer"):
              for field in layer:
                if (j==0):
                  ltable.fields.extend([
                    Field(votable, name=field.tag, datatype="char", arraysize="*")])
                else:
                  try:
                    ltable.get_field_by_id_or_name(field.tag)
                  except:
                    ltable.fields.extend([
                      Field(votable, name=field.tag, datatype="char", arraysize="*")])
                if field.text == None:
                  field.text = "Empty"
                datalay.append(field.text)
                try:
                  i = i + 1
                except:
                  i = 0
              j = 1
            if datalay != []:
              data.append(datalay)
          l = len(ltable.fields)
          nl = int(math.ceil((i)/l)+1)
          dim = nl*l-1
          for x in range(0, nl):
            while len(data[x]) < l:
              data[x].append('Empty')
          try:
            ltable.create_arrays(dim)
            ltable.array = (np.ma.asarray(data,dtype='str'))
            ltable.array.mask = False
          except:
            raise

  votable.to_xml(outfile)

