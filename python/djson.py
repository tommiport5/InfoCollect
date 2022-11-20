#!/usr/bin/python3
'''
Created on 25.03.2020

Encoder and decoder for datetime in json
    based on stackoverflow answers by ramen, Chris Andt and others
@author: Dad
'''

import json
import datetime

class DateTimeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return dict(nested_datetime=obj.isoformat())
        elif isinstance(obj, datetime.date):
            return dict(nested_date=obj.isoformat())
        else:
            return super(DateTimeJSONEncoder, self).default(obj)
        
def datetime_decoder(d):
    if len(d) == 1 and 'nested_datetime' in d: 
        return datetime.datetime.strptime(d['nested_datetime'], '%Y-%m-%dT%H:%M:%S.%f')
    elif len(d) == 1 and 'nested_date' in d: 
        return datetime.date.fromisoformat(d['nested_date'])
    result = {}
    for prop in d:
        if isinstance(d[prop], dict):
            result[prop] = datetime_decoder(d[prop])
        else:
            result[prop] = d[prop]
    return result
            
if __name__ == '__main__':
    l = ['foo', 'bar', 12, datetime.datetime.now()]
    j = json.dumps(l, cls=DateTimeJSONEncoder)
    print(j)
    rt = json.loads(j, object_hook=datetime_decoder)
    print(rt)
    cpl = ['nix', dict(nix='quatsch', garnix=5)]
    cpj = json.dumps(cpl, cls=DateTimeJSONEncoder)
    print(cpj)
    cprt = json.loads(cpj, object_hook=datetime_decoder)
    print(cprt)
    cpl2 = ['nix', dict(nix='quatsch', garnix=5, egal=datetime.datetime.now())]
    cpj = json.dumps(cpl2, cls=DateTimeJSONEncoder)
    print(cpj)
    cprt = json.loads(cpj, object_hook=datetime_decoder)
    print(cprt)
    print(json.loads(j, object_hook=datetime_decoder))