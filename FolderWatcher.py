#!/usr/bin/env python
# coding: utf-8

"""
Notes:
1. I used pandas DataFrame, as in python it is simpler to use than arrays and tables.
However, in other languages I would just create 2D array.
The way of retrieving data is still very similar.
2. For deletions part: 
If a folder contained files and other folders within and got deleted, 
then change message is sent to each element and not only thisparent folder.
It was a decision, as for files we mention backup copy sotred on local (just in case).
3. Similar to 2 -> moved and added is 
""" 

import EventManager as evm
import Helper as h
import asyncio
import os
import uuid
import shutil
import pandas as pd
import time as t
from datetime import datetime as dt

    
def changes_within_file(changed_file, original_file, last_modified_ts):
    """
    Functions compares 2 files line by line and triggers changeDetected event
    """
    nf = open(changed_file)
    new_file = nf.readline()
    of = open(original_file)
    old_file = of.readline()
    line_no = 1
    mes = []
   
    mes.append(last_modified_ts + ":   CONTENT CHANGES in '" + 
               changed_file + "'") 
    mes.append("                            " + \
               "----------------------------------------------")
   
    # this flag is to handle 1 new line -> not to display alert
    # as \n i added to previous (which porgram doesn't dispay), but the next
    # line has only end, not \n, so content change is displayed empty
    line_change = False
    # while reading at least one of 2 files
    while new_file != '' or old_file != '':
        if old_file != new_file:
            # If a line doesn't exist in old file,
            # then those records are deleted
            if new_file == '' and old_file != '':
                line_change = True
                mes.append("                            " + \
                    "deleted "+ "line# " + str(line_no) + ":   " + \
                    old_file)  
            # If a line doesn't exist on new_file, then those records are added
            elif old_file == '' and new_file != '':
                line_change = True
                mes.append("                            "+ \
                    "added "+ "line# " + str(line_no) + ":   " + \
                    new_file) 
            # otherwise output the line on file2 and mark it with < sign
            elif old_file.rstrip("\n\r") != new_file.rstrip("\n\r"): 
                line_change = True
                mes.append("                            "+\
                    "modified " +"line# " + str(line_no) + ":")
                mes.append("         from: " + old_file + "           to: " + \
                           new_file)
        new_file = nf.readline()
        old_file = of.readline()
        line_no += 1
        
    mes.append("                            "+\
               "----------------------------------------------")
    #trigger event
    if line_change == True:
        evm.trigger("changeDetected", mes)
    

def check_element_updates(elem, i):
    # parameter i is index for the record in prev_struc - needed to update and 
    # easier operations
    global prev_struc
   
    # name change -> moved, renamed, both
    if prev_struc.name[i] != elem[0]:
        orig_name = prev_struc.name[i].rsplit(os.sep,1)
        cur_name = elem[0].rsplit(os.sep,1)
        
        if orig_name[0] == cur_name[0] and orig_name[1] != cur_name[1]:
            evm.trigger("changeDetected", [dt.fromtimestamp(elem[2]).ctime() \
                + ":   " + "'" + prev_struc.name[i] + "' got renamed to '" + \
                cur_name[1] + "'"])
        elif orig_name[0] != cur_name[0] and orig_name[1] == cur_name[1]:
            evm.trigger("changeDetected", [dt.fromtimestamp(elem[2]).ctime() \
                + ":   " + "'" + orig_name[1] + "' got moved from '" + \
                orig_name[0] + "' to '" + cur_name[0] + "'"])
        else:
            evm.trigger("changeDetected", [dt.fromtimestamp(elem[2]).ctime() \
                + ":   " + "'" + prev_struc.name[i] + \
                "' got renamed and moved to '" + elem[0] + "'"])
        # update name in prev_struc
        prev_struc.at[i, 'name'] = elem[0]

    # last modified timestamp change -> content change
    if prev_struc.type[i] == 'file' and prev_struc.last_modified[i] != elem[2]:
        # update last modified date
        prev_struc.at[i, 'last_modified'] = elem[2]
        # what are changes?
        changes_within_file(elem[0], prev_struc.file_copy[i], \
                            dt.fromtimestamp(elem[2]).ctime())
        shutil.copy(elem[0], prev_struc.file_copy[i])
    
    
def check_additions(elem):
    global prev_struc
    copy_name = ''
    # if file, make a local copy
    if (elem[3] == 'file'):
        copy_name = h.create_localstorage_copy(elem[0])
    # add new record into prev_struc
    row = {'name': elem[0], 'id': elem[1], 'last_modified': elem[2], \
           'type': elem[3], 'file_copy': copy_name}  
    prev_struc = prev_struc.append(row, ignore_index=True)
    # trigger event
    evm.trigger("changeDetected", [dt.fromtimestamp(elem[2]).ctime() + \
        ":   " + elem[3] + " '" + elem[0] + "' is added"])
    
    
def check_deletions(deleted_files):
    """
    Triger changeDetected event to alert about deleted folders or files.
    For all deleted files - message includes the name of the file copy 
        in local storage.
    For folders - just message about the event.
    """
    global prev_struc
    for dfile in deleted_files:
        if (dfile != ''):
            parent_folder = dfile.rsplit(os.sep,1)[0]
            # if parent folder is in deleted_files, 
            # then it will be a part of wrapping some folder later, so skip 
            if (parent_folder not in deleted_files):
                ind = prev_struc[prev_struc.name == dfile].index.to_list()[0]
                mts = dt.fromtimestamp(prev_struc[prev_struc.name == parent_folder].last_modified).ctime()
                # only files was deleted
                if (prev_struc.type[ind] == 'file'):
                    evm.trigger("changeDetected", [mts + ":   '" + dfile + \
                        "' is deleted or moved outside of watched folder. " + \
                        "Back up copy is " + \
                        prev_struc.file_copy[ind]])   
                    prev_struc.drop(ind, inplace=True)
                else:
                    elems_within = list(filter(lambda x: dfile in x, deleted_files))
                    # only empty folder was deleted
                    print(elems_within)
                    if (len(elems_within) == 1):
                        evm.trigger("changeDetected", [mts + ":   '" + dfile + \
                            "' is deleted or moved outside of watched " + \
                            "folder. Folder was empty"])   
                        prev_struc.drop(ind, inplace=True)
                    # folder with data inside was deleted
                    else:
                        elems_within.remove(dfile)
                        msg = []
                        msg.append(mts + ":   '" + dfile + "' is deleted or " + \
                            "moved outside currently watched folder. Folder" + \
                            " had files: ")
                        prev_struc.drop(ind, inplace=True)
                        # get all files/folders within
                        for elem in elems_within:
                            ind = prev_struc[prev_struc.name == elem].index\
                                .to_list()[0]
                            # if folder, just drop
                            if (prev_struc.type[ind] == 'folder'):
                                prev_struc.drop(ind, inplace=True)
                                # overwrite value to know that we already alerted 
                                # about this element
                                # in case this element is later in the 1st loop 
                                # of this function
                                deleted_files[deleted_files.index(elem)] = ''
                            # if file, add filename and copy name to message 
                            else:
                                msg.append("* '" + elem + "' with backup " + \
                                    prev_struc.file_copy[ind])
                                prev_struc.drop(ind, inplace=True)
                                deleted_files[deleted_files.index(elem)] = ''
                        evm.trigger("changeDetected", msg)   
    
    
async def watchFolder(filepath):
    global prev_struc
    retry = 0
    try:
        # original setup/data to check against
        prev_struc = pd.DataFrame(columns=['name', 'id', 'last_modified', \
                                           'type', 'file_copy'])

        """ 
        unwrap all sub-directories and get info for each file and folder 
        info is: name, system ids, last modified date in seconds, 
            type = file/folder, name of a file copy  
        create a copy for each file in ./localstorage
        """
        prev_struc = h.unwrap_folder_with_stats(filepath, True)
        
        # while watched folder/file exists
        while len(prev_struc) != 0:
            try:
                cur_struc = h.unwrap_folder_with_stats(filepath, False)
                for index, elem in cur_struc.iterrows():
                    # elem is 1D array with 
                    # [name, id, last_modif, type, copy_name]
                    # if file already existed in prev structure - 
                    # check by system id, as it doesn't change
                    i = prev_struc[prev_struc.id == elem[1]].index.to_list() 
                    if i != []:
                        i = i[0] 
                        # MODIFICATION - renames, moves, file content changes
                        # update prev_struc with changes
                        check_element_updates(elem.to_list(), i)
                    else:
                        # ADDITIONS
                        # add new row in prev_struc and create a file copy 
                        check_additions(elem.to_list())

                # DELETIONS 
                # as prev_struc is updated with modifications and additions 
                # we can easily compare prev_struc and cur_struc to know 
                # what elements got deleted
                deleted_files = set(prev_struc.name.to_list()) - set(cur_struc.name.to_list())
                deleted_files = prev_struc[prev_struc.name.isin(deleted_files)].name.to_list()
                if (len(deleted_files) != 0):
                    check_deletions(deleted_files)
                    
                retry = 0
                #await asyncio.sleep(1)
            except FileNotFoundError:
                # sometimes changes are not picked up together: 
                # for example, a file got renamed and had changes inside)
                # changes got picked, but renamed not yet
                # this will thrown an exception, but if we retry, 
                # it should continue working fine and picked the rename
                if retry == 3:
                    raise
                retry += 1
                continue   
    except KeyboardInterrupt:
        print("---------------------------------------------------------------------")
        print("The program is TERMINATED") 
    except FileNotFoundError:
        print("---------------------------------------------------------------------")
        print("ERROR: The folder which is supposed to be watched got deleted or moved") 
    except Exception as e:
        print("---------------------------------------------------------------------")
        print("ERROR: " + e ) 
    finally:
        print("---------------------------------------------------------------------")
        print('EXIT: Stop watching folder')
        print("---------------------------------------------------------------------")
        
evm.add("startWatcher", watchFolder, "async")

