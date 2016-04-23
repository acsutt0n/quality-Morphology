#!/usr/bin/python

# usage: ./knossosNumNodes.py nml_file log_file
# Get the number of nodes in an nml_file and add it (with the nml_file name)
#    to the log_file. Also get the time. Assumes "active node" is last node.
# This is backwards-compatible with python2-3


import sys, os


def get_properties(fname):
  """
  """
  num_nodes, time_ms = None, None
  with open(fname, 'r') as fIn:
    for line in fIn:
      if line:
        try:
          splitLine = line.strip().split('=')
          if splitLine[0] == '<time ms':
            time_split = line.split('"')
            time_ms = int(time_split[1])
          elif splitLine[0] == '<activeNode id':
            node_split = line.split('"')
            num_nodes = int(node_split[1])
          else:
            pass
        except:
          pass
      # Break out if we have everything
      if num_nodes is not None and time_ms is not None:
        return num_nodes, time_ms
  print('Only found -- num_nodes: %i, time_ms: %i' 
        %(int(num_nodes), int(time_ms)))
  return num_nodes, time_ms



def write_properties(fname, logname):
  """
  """
  num_nodes, time_ms = get_properties(fname)
  add_line = '%s,%i,%i' %(fname, num_nodes, time_ms)
  with open(logname, 'a') as log:
    log.write(add_line)
    log.write('\n')
  return



#####################
if __name__ == "__main__":
  args = sys.argv
  if len(args) < 3:
    print('Need: nmlfile, logfile')
    sys.exit()
  if 'ml' not in args[1]: # .xml or .nml
    print('nml/xml file needed for argument 1; skipping')
    sys.exit()
  write_properties(args[1], args[2])

  
  






