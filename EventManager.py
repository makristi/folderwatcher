#!/usr/bin/env python
# coding: utf-8

events = {}

def add(event, func, sync_flag = "sync"):
    # sync_flag have 'sync', 'async' values for now
    if event not in events:
        events[event] = {}
    if sync_flag not in events[event]:
        events[event][sync_flag] = []
    events[event][sync_flag].append(func)

def delete(event):
    if event in events:
        del events[event]
        
def delete_all():
    all_events = list_all()
    if (all_events != 'None'):
        for event in all_events:
            delete(event)
        
def list_all():
    if len(events) == 0:
        return ['None']
    else:
        return list(events.keys())

async def async_trigger(event, data): 
    sync_flag = "async"
    if (len(events) != 0):
        for event in list(events.keys()):
            if sync_flag in events.get(event):
                for func in events.get(event).get(sync_flag):
                    await func(data)

def trigger(event, data):  
    sync_flag = "sync"
    if (len(events) != 0):
        for event in list(events.keys()):
            if sync_flag in events[event]:
                for func in events[event][sync_flag]:
                    func(data)
