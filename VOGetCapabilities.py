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

################## MM: add logger for debug
import logging       # this will allow logging from within a module
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
logger.addHandler(ch)
#logger.debug('This is a test log message.')#M: test that logger works
######################
# to reload module say: 
# importlib.reload(VOGetCapabilities) 
# to use function use
# VOGetCapabilities.VOGetCapabilities('WMSgetcapabilities.xml','VOWMSgetcapabilities.xml')
######################

def VOGetCapabilities(filename,outfile):
  votable = VOTableFile()
  parser = ElementTree.XMLParser(recover=True)
  f = codecs.open(filename,'r','utf-8')
  string = f.read()
  string = bytes(bytearray(string, encoding='utf-8')) ## force utf-8 encoding even if xml says otherwise
  root = ElementTree.fromstring(string, parser)
  for element in root:
    res = element.tag
    resid = str(res).split('}')[-1:][0] # MM, note that we have to convert res to string first
#    logger.debug(resid) ## debug
#    if (res!=ElementTree.Comment):
    if (resid!=str(ElementTree.Comment)): # MM
#      resid=re.sub(':','_',res)
      resid=re.sub(':','_',resid)
      resource = Resource(name=res,ID=resid)
      votable.resources.append(resource)
      table = Table(votable)
      resource.tables.append(table)
      for param in element:
        par = param.tag
        parid=str(par).split('}')[-1:][0] # MM
        value = param.text
        if value is None:
          listvalue=param.items()
          value=listvalue
        dt=type(value).__name__
        if (dt=="str"):
          dt="char"
          arraysize="*"
          table.params.extend([
#            Param(votable, name=par, datatype=dt, value=value)])
            Param(votable, name=parid, datatype=dt, value=value)])
        elif (dt=="list"):
          if (len(value)>0):
            for tup in value:
              table.params.extend([
#                Param(votable, name=tup[0], datatype="char", value=tup[1])])
                Param(votable, name=tup[0].split('}')[-1:][0], datatype="char", value=tup[1])])
#        if (par=="Layer"):
        if (parid=="Layer"):
#          lresource = Resource(name=par,ID=par)
          lresource = Resource(name=par,ID=parid) # MM
          votable.resources.append(lresource)
          ltable = Table(votable)
          lresource.tables.append(ltable)
          j = 0
          data = []
          for layer in param:
            lay = layer.tag
            layid = str(lay).split('}')[-1:][0] # MM
            datalay = []
#            if (lay=="Layer"):
            if (layid=="Layer"): # MM
              for field in layer:
                fieldid=str(field.tag).split('}')[-1:][0]
                if (j==0):
                  ltable.fields.extend([
#                    Field(votable, name=field.tag, datatype="char", arraysize="*")])
                    Field(votable, name=fieldid, datatype="char", arraysize="*")])
                else:
                  try:
#                    ltable.get_field_by_id_or_name(field.tag)
                    ltable.get_field_by_id_or_name(fieldid)
                  except:
                    ltable.fields.extend([
#                      Field(votable, name=field.tag, datatype="char", arraysize="*")])
                      Field(votable, name=fieldid, datatype="char", arraysize="*")])
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
#          nl = int(math.ceil((i)/l)+1) #this will only work if there are no nested layers
#          print(nl) # so i'm commenting this out and replacing with simple len(data)
          nl=len(data) #MM
#          logger.debug(nl) ## debug
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

