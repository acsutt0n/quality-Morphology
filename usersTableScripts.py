# Simple scripts to convert the users csv file into a cleaned data frame

"""
The users table takes the form:
878_067_GM(Adriane),rh,3/09/16,118-121
   Where the fist element MUST match the cell_name in nodedf

This package helps convert these data (which are easy to record & type)
into file-unique data that can be passed to SQL.
"""


import numpy as np
import pandas as pd
import sqlite3
import datetime as dt


########################################################################
# Helper functions

def make_dt(date, ez=True):
  """ Try to make a datetime string for sql to read """
  if ez: # mm/dd/yy
    m, d, y = date.split('/')
    y = '20'+y
    date = '-'.join([y,m,d])
  return date



########################################################################
# 'Core' functions

def get_fileroot(nodedf):
  """
  Get the root (common part) of all filenames.
  a nodedf row is: 
         cellname                      filename  id  num_nodes  time_ms  cell_id  file_id
  0  768_061_ch00  skeleton-031215-1410.001.nml   0        140   595065        8        0
  """
  roots, exts = {}, {}
  # Get the roots
  for r in range(nodedf.cell_id.max()+1):
    root, ext = None, None # No spillover
    # Don't want 'targets' to be the root since there aren't any logged!
    moveon, cnt = False, 0
    
    while not moveon:
      idx = nodedf[nodedf.cell_id==r].index.values[cnt] # check this one
      try:
        rsplit = nodedf.filename[idx]
      except:
        rsplit = nodedf.file_name[idx]
      rsplit = rsplit.split('.')
      root, ext = rsplit[0], rsplit[-1]
      if 'target' not in root:
        moveon = True
      else:
        cnt += 1
    
    if nodedf.cellname[idx] not in roots.keys():
      roots[nodedf.cellname[idx]] = root
      exts[nodedf.cellname[idx]] = ext
  print('Got all %i roots (and %i extensions)' %(len(roots), len(exts)))
  return roots, exts



def build_filenames(nodedf, userdf):
  """
  Build what each specific filename should be from the users df,
  created by the nodes df.
  """
  def serials(serialstring):
    # Break a range of ints into ### numbers
    if '-' not in serialstring:
      try:
        return [serialstring]
      except:
        print('could not make an int from ' + serialstring)
        return [None]
    r0, r1 = serialstring.split('-')
    serial_ = list(range(int(r0), int(r1)+1)) # Convert to int and make range
    serial_ = [str(s) for s in serial_]
    for s in range(len(serial_)):
      while len(serial_[s]) < 3: # or ##, but not ###
        serial_[s] = '0' + serial_[s] # Add leading 0
    return serial_
  
  user_ids = {}
  # Get the roots and extensions
  roots, exts = get_fileroot(nodedf)
  # Initialize the new dict
  files = {'cell_name': [], 'file_name': [], 'date': [], 
           'user_name': [], 'user_id': [], 'cell_id': [],
           'file_id': []}
  
  # This iterates through the USER DF
  for f in range(userdf.shape[0]):
    serial_ = serials(userdf.files[f])
    files_s = []
    for s in serial_:
      try:
        files_s.append('.'.join([roots[userdf.cell_name[f]], s,
                                  exts[userdf.cell_name[f]]]))
      except:
        print('Looking for %s in' %userdf.cell_name[f])
        print(roots.keys())
    
    # Check if each of these files exists
    for fil in files_s:
      if fil in list(nodedf.filename.values): # Log it
        # node_idx refers to NODE DF -- f refers to USER DF
        node_idx = list(nodedf.filename.values).index(fil)
        files['cell_name'].append(userdf.cell_name[f])
        files['cell_id'].append(nodedf.cell_id[node_idx])
        files['file_id'].append(nodedf.file_id[node_idx])
        files['file_name'].append(fil)
        files['date'].append(userdf.date[f])
        
        # Create a new user_id if it's a new user
        usr = userdf.user_name[f]
        if usr not in user_ids.keys():
          user_ids[usr] = len(user_ids.keys())
        files['user_name'].append(usr)
        files['user_id'].append(user_ids[usr])
      else:
        print('Could not find a match for %s' %fil)
    # Finished this round of files
  # Finished iterating through user df
  
  return pd.DataFrame.from_dict(data=files, orient='columns')

#


def df_to_sqltable(df, cursor, table_name, types, columns=None, force=True):
  """
  _cursor_ is sqlite3.connect('db_file.db').cursor()
  If _columns_ is None, df columns are used; else, only the first
  len(_columns_) columns of df are used with the names given in _columns_
  * Use df.drop([unwanted1, unwanted2, ...], axis=1) to make this easier.
  """
  if df.shape != df.dropna().shape:
    print('Get NaNs out of this df'); return None
  # The type-dict
  typedict = {'int': int, 'real': float, 'text': str, 'date': make_dt}
  if columns is None:
    columns = df.columns
  if np.prod([1 if t in typedict.keys() else 0 for t in types]) == 0:
    print('Types must be either int, real, text or date'); return None
  if len(columns) != len(types):
    print('Need explicit columns (%i)  and types (%i), should be equal'
           %(len(columns), len(types))); return none
  
  # Make the table
  if not table_name.isalnum():
    print('Table name must be alphanumeric only'); return None
  if force:
    cursor.execute('drop table if exists %s' %table_name)
  items_string = ', '.join([' '.join([str(x), str(y)]) for x,y in zip(columns, types)])
  table_string = '''create table %s (%s)''' %(table_name, items_string)
  try:
    cursor.execute(table_string)
  except:
    print('Invalid table string: %s' %table_string); return None
  
  # Add the entries to the table
  entries = []
  for i in range(df.shape[0]):
    entries.append([typedict[types[x]](df[df.columns[x]][i]) for x in range(len(columns))])
  exec_string_ = ','.join(['?' for i in columns])
  exec_string = 'insert into %s values (%s)' %(table_name, exec_string_)
  try:
    cursor.executemany(exec_string, entries)
  except:
    print('Some problem executing many -- %s' %exec_string)
    print(entries[0])
    print([type(ent) for ent in entries[0]]); return None
  print('Changes HAVE NOT been commited; commit changes if the table looks right')
  return

#

def nodes_added(df):
  """ Calculate the nodes added in a skeleton file. """
  curr_cell, curr_node, curr_time = None, None, None
  nodes_diff, time_diff = [], []
  # Iterate through the data frame's values
  for i in range(df.shape[0]):
    if df.cellname.values[i] == curr_cell: # Same as active file
      nodes_diff.append(df.num_nodes.values[i] - curr_node)
      curr_node = df.num_nodes.values[i]
      time_diff.append(df.time_ms.values[i] - curr_time)
      curr_time = df.time_ms.values[i]
    else: # A new cell (or the first cell)
      curr_cell = df.cellname.values[i] # Set the new cell
      nodes_diff.append(df.num_nodes.values[i])
      curr_node = df.num_nodes.values[i]
      time_diff.append(0) # Not really accurate but real way is too long
      curr_time = df.time_ms.values[i]
  # Now len(_diff) lists should equal df.shape[0]
  return nodes_diff, time_diff




######################################################################
if __name__ == "__main__":
  print('Module is used interactively')


























