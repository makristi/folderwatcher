#!/usr/bin/env python
# coding: utf-8

import EventManager as evm
import FolderWatcher as fw
import os
import asyncio


def display_message(mes):
    for i in mes:
        print(i)
                     
#def cancel_all_tasks(loop):
    
#    to_cancel = asyncio.all_tasks(loop)
#    if not to_cancel:
#        return

#    for task in to_cancel:
#        print('1')
#        task.cancel()

#    loop.run_until_complete(
#        asyncio.gather(*to_cancel, loop=loop, return_exceptions=True))

#    for task in to_cancel:
#      if task.cancelled():
#           continue
#       if task.exception() is not None:
#           loop.call_exception_handler({
#               'message': 'unhandled exception during asyncio.run() shutdown',
#               'exception': task.exception(),
#               'task': task,
#         })

if __name__ == '__main__':        
    evm.add("changeDetected", display_message)
    filepath = input("Enter folder to watch for changes: ")
    while (os.path.exists(filepath) == False):
        filepath = input("This directory/file doesn't exist. Please, try again: ")
    
    loop = asyncio.new_event_loop()
        
    try:
        loop = asyncio.new_event_loop()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(evm.async_trigger("startWatcher", filepath))
    finally:
        try:
            #ancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()
            evm.delete_all()
          
    