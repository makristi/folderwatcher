#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import os
import glob
import shutil
import uuid
import pandas as pd

# More or less gneric functions
def type_fd(x):
    """
    checks if an element is a file, otherwise, it is a directory
    """
    if os.path.isfile(x):
        return 'file' 
    else:
        return 'folder'
    
def create_file_copy (file, dest_file):
    os.makedirs(dest_file.rsplit(os.sep,1)[0], exist_ok=True)
    shutil.copy(file, dest_file)
    
    
def unwrap_folder(filepath):
    ## find all files and directories within 
    all_files = [filepath]
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*'))
        for f in files :
            all_files.append(os.path.abspath(f))
    return all_files


# Functions related to Folder Watcher 
def create_localstorage_copy(file):
    """ 
    create a copy of a file into local storage 
    uuid is used to create a unique name for a copy. This handles files with 
    same names and different paths and eliminates a concern about paths at all 
    """
    unique_iden = str(uuid.uuid1())
    uniq_filename = './localstorage/' + unique_iden + '.' + file.split('.')[-1]
    create_file_copy(file, os.path.realpath(uniq_filename))
    return uniq_filename


def unwrap_folder_with_stats(filepath, copy_flag = False):
    """
    find all directories and files within filepath
    create table with information needed for tracking 
        (name, system id, last modified date, type - file/folder, 
        name of file copy) about each element 
    if flag 'copy_flag' = True, then created file copy 
    """
    #structure of info table 
    info_table = pd.DataFrame(columns=['name', 'id', 'last_modified', 'type', \
                                       'file_copy'])
    
    element_list = unwrap_folder(filepath)
    # unwraps all elements and add their data to return set
    for element in  element_list:
        # os.stat returns system info about file/folder
        stat = os.stat(element)
        uniq_filename = ''
        if (type_fd(element) == 'file' and copy_flag == True):
            # creates a local copy of the file
            uniq_filename = create_localstorage_copy(element)
        row = {'name': os.path.abspath(element), 'id': stat.st_ino, \
                'last_modified': stat.st_mtime, 'type': type_fd(element), \
                'file_copy': uniq_filename}     
        info_table = info_table.append(row, ignore_index=True)
    
    return info_table

