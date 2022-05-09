import splunk.Intersplunk as si
import splunk.mining.dcutils as dcu

import json
import socket
import csv

import sys
import splunk.search as search
import splunk.entity as entity
from splunk.rest import simpleRequest
import requests


def sendData(results, settings):
    keywords, argvals = si.getKeywordsAndOptions()

    namespace       = settings['namespace']
    owner           = settings['owner']
    sessionKey      = settings['sessionKey']
    sid             = settings['sid']

    
    jobResponseHeaders = {} 
    jobResponseBody = { 
        'entry': [
            {
                'content': {}
            }
        ]
    }
    if sid: 
        uriToJob = entity.buildEndpoint(
            [
                'search', 
                'jobs', 
                sid
            ], 
            namespace=namespace, 
            owner=owner
        )
        jobResponseHeaders, jobResponseBody = simpleRequest(uriToJob, method='GET', getargs={'output_mode':'json'}, sessionKey=sessionKey)
    
    searchJob         = json.loads(jobResponseBody)
    jobContent        = searchJob['entry'][0]['content']
    # add results into jobContent object
    jobContent['results'] = []
    for rwt in results:
        jobContent['results'].append(dict(rwt)) # need to convert or else json.dumps doesn't work

    # send to tcp port
    try:
        headers = {'Authorization':''}
        headers['Authorization'] = 'Splunk ' + sessionKey  
        response = requests.post('https://localhost:8089/services/receivers/simple?index=spl_bee&sourcetype=response', headers=headers, data=json.dumps(jobContent), verify=False)
        print(response)
    except requests.exceptions.RequestException as e:
        si.generateErrorResults('%s while sending data' % (str(e)))
        sys.exit(-1)

    return results

settings = {}

results = si.readResults(None, settings)

try:
    results = sendData(results, settings)
except Exception as e:
    si.generateErrorResults(str(e))
    sys.exit(-1)
    
si.outputResults(results)
