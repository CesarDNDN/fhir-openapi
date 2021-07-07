# Functions used for converting input swagger into output OpenAPI
import json
import os
import sys

def configureNewSwagger(source):
    """
    Initializes the new json file and removes deprecated keys present in old json file
    """
    target = json.loads(json.dumps(source))

    # Switch from swagger to openapi
    target.pop('swagger')
    target['openapi'] = '3.0.1'
    
    #move the scheme/host/basepath to the server block
    scheme = target.pop('schemes')[0]
    host = target.pop('host')
    basePath = target.pop('basePath')
    print(host)
    print(basePath)
    host = "fhir.pskykpxb.static-test-account.isccloud.io"
    target['servers'] = [{'url':scheme+"://"+host+basePath}]

    #move the definitions into a different subpath
    definitions = target.pop('definitions')
    target['components'] = {}
    target['components']['schemas'] = definitions

    return target


def moveParameters(target):
    """
    Iterate through all paths and move the parameter types to the schema subsection
    """
    for path in target['paths']:
        for verb in target['paths'][path]:
            #Only need to be performed on 'parameters' key
            if verb == 'parameters':
                paramtype = target['paths'][path][verb][0].pop('type')
                target['paths'][path][verb][0]['schema'] = {'type':paramtype}

    return target

def moveVerbTypes(target):
    """
    Iterate through all paths and shift the verb parameters to the schema
    """
    for path in target['paths']:
        for verb in target['paths'][path]:
            # post and put removes parameters verb later on, skip for now. Parameters verb doesn't have parameters
            if verb in {'post','put','parameters'}:
                continue
            for parameterId in range(len(target['paths'][path][verb]['parameters'])):
                # shifting the verb type into the schema block
                verbtype = target['paths'][path][verb]['parameters'][parameterId].pop('type')
                target['paths'][path][verb]['parameters'][parameterId]['schema'] = {'type':verbtype}
                # shifting the verb format into the schema block (IF PRESENT)
                if 'format' in target['paths'][path][verb]['parameters'][parameterId]:
                    format = target['paths'][path][verb]['parameters'][parameterId].pop('format')
                    target['paths'][path][verb]['parameters'][parameterId]['schema']['format'] = format
    return target


def addRequestBody(target):
    """
    Iterate through all paths and add the request body to post/put commands
    """
    for path in target['paths']:
        for verb in {'post','put'}:
            if verb in target['paths'][path].keys():
                # remove parameters flag if present
                target['paths'][path][verb].pop('parameters') if 'parameters' in target['paths'][path][verb].keys() else None
                # remove consumers flag if present
                target['paths'][path][verb].pop('consumes') if 'consumes' in target['paths'][path][verb].keys() else None
                # add requestBody flag
                target['paths'][path][verb]['requestBody'] = {  "content": {
                        "application/fhir+json": {
                            "schema": {"$ref": '#/components/schemas/'+path.split('/')[1]}
                        }
                }}
    return target


def addResponseBody(target):
    """
    Iterate through all paths, and append content if the verb is 'get'
    """
    for path in target['paths']:
        for verb in target['paths'][path]:
            # skip 'parameters', since no responses for 'parameters'
            if verb == 'parameters':
                continue
            for response in target['paths'][path][verb]['responses']:
                # content is dependent on resource type (individual vs plural)
                resource = path.split('/')[1]


                if verb != 'get':
                    content = {}
                elif path == '/'+response or path == '/'+resource+'/{id}/_history':
                     content= { "application/fhir+json": {"schema": {"type":"array","items":{"$ref": '#/components/schemas/'+resource}} }}
                else:
                    content= { "application/fhir+json": {"schema": {"$ref": '#/components/schemas/'+resource} }}
                # appending the content to the correct spot
                target['paths'][path][verb]['responses'][response]['content'] = content
                # removing any schema associated with the response
                target['paths'][path][verb]['responses'][response].pop('schema') if 'schema' in target['paths'][path][verb]['responses'][response].keys() else None
            target['paths'][path][verb]['responses']['400'] = {'description': "Invalid"}
            target['paths'][path][verb]['responses']['404'] = {'description': "Not-Found"}
            target['paths'][path][verb]['responses']['406'] = {'description': "Not-Supported"}
            target['paths'][path][verb]['responses']['503'] = {'description': "Operation"}
            target['paths'][path][verb]['responses']['401'] = {'description': "Unauthorized"}
            target['paths'][path][verb]['responses']['403'] = {'description': "Forbidden"}
            target['paths'][path][verb]['responses']['415'] = {'description': "Unsupported-Type"}
            target['paths'][path][verb]['responses']['500'] = {'description': "Internal-Error"}
            target['paths'][path][verb]['responses']['502'] = {'description': "Bad-Gateway"}
    return target



