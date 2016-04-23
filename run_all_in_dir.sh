#!/bin/bash

# Run knossosNumNodes.py for all files in a given directory?
# ./run_all_in_dir.sh dirname log_file


# Briefly check inputs
if [ $# -ne 2 ] ; then
  echo "Need: directory of xml/nml files & node log file" 
fi


# Load the directory objects line-by-line and run the script
# Get the files
ls *ml $1 > filelist.txt
filelist="filelist.txt"
# Read the file list and run the python program
slash="/"
while IFS='' read -r line || [[ -n "$line" ]]; do
  newname="$(pwd)$slash$line" # Make the file path
  ./knossosNumNodes.py $newname $2 # Get the num nodes and time
done < "$filelist"


