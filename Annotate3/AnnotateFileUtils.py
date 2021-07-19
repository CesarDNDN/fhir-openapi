import json
import os

def getParamDesc(searchParams,resourceName,parameterName):
    """
    Find the description in the search parameters given a resource and a parameter
    """
    # filter out preliminary forward slash
    if resourceName[0] == '/':
        resourceName=resourceName.split('/')[1]
    # get first description filtered by the parameter name
    description = [entry['resource']['description'] for entry in searchParams['entry'] if entry['resource']['id'].lower() == resourceName.lower()+'-'+parameterName.lower()]
    if not description:
        description = [entry['resource']['description'] for entry in searchParams['entry'] if entry['resource']['name'].lower() == parameterName.lower() and entry['resource']['description'][:19] == 'Multiple Resources:']
    if description and description[0][:19] == 'Multiple Resources:':
        # There can be multiple multiple resources.
        description = '\r\n'.join(description)
        description = [resource[resource.index('): ')+3:resource.index('\r\n')] for resource in description.split('[') if resource[:len(resourceName)].lower()==resourceName.lower()]
    description = '' if len(description) == 0 else description[0]  
    return description

def getElementDesc(dataElements,resourceName,parameterName):
    """
    Find the description in the data elements given the resource and parameter.
    """
    try:
        # get first description filtered to match the resource and parameter name
        # ASSUMPTION: ONLY ONE DESCRIPTION PER RESOURCE+PARAMETER COMBO
        if resourceName.lower()+"."+parameterName.lower() == 'activitydefinition.product':
            print("Found it")
        description = [(entry['resource']['snapshot']['element'][0]['definition'],entry['resource']['snapshot']['element'][0]['short']) for entry in dataElements['entry'] if entry['resource']['name'].lower()==resourceName.lower()+"."+parameterName.lower()][0]
        # TODO use default definition unless exceed 50 CHAR
        description = description[0] if len(description[0]) < 100 else description[1] 
    except Exception as e:
        # If no key matches the combination, setting description to following:
        if resourceName.lower()+"."+parameterName.lower() == 'activitydefinition.product':
            print("It threw an error!")
        description = ""
    return description


def getProfileDesc(profileResources,resourceName):
    """
    Find the description in the profile resources given the resource
    """
    try:
        # get first description filtered to match the resource
        # ASSUMPTION: ONLY ONE DESCRIPTION PER RESOURCE IN PROFILE RESOURCES
        description = [entry['resource']['snapshot']['element'][0]['short'] for entry in profileResources['entry'] if entry['resource']['name'].lower()==resourceName.lower()][0]
    except Exception as e:
        # If no key matches the resources, setting description to the following:
        description=""
    return description    


def getProfileElementDesc(profileResources,resourceName,element):
    """
    Find the description of an element given the resource and element
    """
    try:
        # first extract topLevel resource name EX: Patient.Gender -> Patient
        topLevelResourceName = resourceName.split(".")[0]
        # get the block related to the topLevel resource name
        toplevel = [entry['resource']['snapshot']['element'] for entry in profileResources['entry'] if entry['resource']['name'].lower() == topLevelResourceName.lower()][0]
        # get the description from the topLevel block given the resource+element combination
        description = [entry['short'] for entry in toplevel if entry['id'].lower()==resourceName.lower()+"."+element.lower()][0]
    except Exception as e:
        # If no key matches the resource+element combination, setting description to the following:
        description = "UNABLE TO FIND RESOURCE/ELEMENT NAME"
    return description


def removeFormatParam(swagger):
    for id in range(len(swagger['tags'])):
        # Paths are prefaced with forward slash
        idName = '/'+swagger['tags'][id]['name']
        # Filter out Capability statement 
        if idName != '/CapabilityStatement':
            formatId = len(swagger['paths'][idName]['get']['parameters'])-1
            if swagger['paths'][idName]['get']['parameters'][formatId]['name'] == '_format': # Should always pass, verification
                swagger['paths'][idName]['get']['parameters'].pop(formatId)
    return swagger


def setSwaggerParamDesc(swagger,searchParams):
    """
    Set the Swagger GET Parameter Description to what is stored in the search Parameters using helper function
    """
    for id in range(len(swagger['tags'])):
        # Paths are prefaced with forward slash
        idName = '/'+swagger['tags'][id]['name']
        # Filter out Capability statement 
        if idName != '/CapabilityStatement':
            for paramId in range(len(swagger['paths'][idName]['get']['parameters'])):
                # Get the parameter name to use getParamDesc function
                paramName = swagger['paths'][idName]['get']['parameters'][paramId]['name']
                # Set description to what is returned from search Parameters
                swagger['paths'][idName]['get']['parameters'][paramId]['description'] = getParamDesc(searchParams,idName,paramName)
    swagger = removeFormatParam(swagger)
    return swagger


def setIrisDefinitions(swagger,irisDefinitions):
    """
    setting the components to the schemas generated from the ObjectScript code
    """
    swagger['components'] = {"schemas":irisDefinitions}
    return swagger

def setSchemas(swagger,irisDependencies,profileResources,dataElements):
    """
    Setting the schemas of each of the definitions based on the dependencies generated from ObjectScript code
    """
    for definition in swagger['components']['schemas']:
        # Set Description to what is stored in the profile resources for description
        swagger['components']['schemas'][definition]['description'] = getProfileDesc(profileResources,definition)
        for propert in swagger['components']['schemas'][definition]['properties']:
            # Set the property description to what is stored in the data elements object
            propertyDesc = getElementDesc(dataElements,definition,propert) if definition in irisDependencies.keys() else getProfileElementDesc(profileResources,definition,propert)
            # print(definition,propert)
            swagger['components']['schemas'][definition]['properties'][propert]['description'] = propertyDesc
    return swagger

def setSecurity(swagger):
    """
    Set up security in the openapi file
    """
    # Set the security scheme to necessary structure
    # Anton Azure AD tenant: b103c5f1-f287-4752-b5d3-b8219709fb91
    # Anton Client ID: 25671b8e-69be-4128-bea1-8c6260678220 (need to be set in Swagger-ui.html)        
    # ISC Azure AD tenant: 74abaa74-2829-4279-b25c-5743687b0bf5
    # ISC Client ID: 3ef0a392-0348-4a50-9b7a-c4fb9a67e6b3 (need to be set in Swagger-ui.html)
    # Cesar API Key (CesarTestKey): RtHnhGLdRu5g96YBbxJBiadEoPjkZMUR76OJi915
    swagger['components']['securitySchemes'] = {}
    swagger['components']['securitySchemes']['ApiKeyAuth'] = {
            "type":"apiKey",
            "in": "header",
            "name": "X-API-Key"}
    swagger['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
    # Set the security for each of the tags to accept put/get/post/delete
    for id in range(len(swagger['tags'])):
        # Paths are prefaced by a '/'
        idName = '/'+swagger['tags'][id]['name']
        # Filter out security for Capability Statement
        if idName != '/CapabilityStatement':
            swagger['paths'][idName]['post']['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
            swagger['paths'][idName]['get']['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
            swagger['paths'][idName+'/{id}']['put']['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
            swagger['paths'][idName+'/{id}']['delete']['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
            swagger['paths'][idName+'/{id}']['get']['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
            swagger['paths'][idName+'/{id}/_history']['get']['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
            swagger['paths'][idName+'/{id}/_history/{vid}']['get']['security'] = [ { "ApiKeyAuth":["user/*.write","user/*.*"] } ]
    return swagger


def saveSwagger(swagger,filePath,subsetPath,profileResources,irisDependencies):
    """
    save the new openapi spec and the subset specs
    """
    try:
        # open the save file path and dump json contents
        with open(filePath,'w') as f:
            json.dump(swagger,f)
        #setting up subset json contents
        for id in range(len(swagger['tags'])):
            idName = swagger['tags'][id]['name']
            swaggerSubset = swagger.copy()
            # description for the subset set as description from profile resources
            swaggerSubset['info']['description']=getProfileDesc(profileResources,idName)
            swaggerSubset['info']['title'] = 'FHIR R4 '+idName+' Resource'
            # modify name for paths
            idName = '/'+idName
            # print(idName)
            # Adjust paths to only contain paths relevant to the ID
            if idName == '/CapabilityStatement':
                continue #### SKIPPING CAPABILITY STATEMENT, ADDRESS WITH PATRICK ####
            swaggerSubset['paths'] = {key:swagger['paths'][key] for key in {idName,idName+'/{id}',idName+'/{id}/_history',idName+'/{id}/_history/{vid}'}}
            idName = idName[1:]
            # print(idName)
            # Adjust tags to only contain the name of ID
            swaggerSubset['tags'] = [{'name':idName}]
            # Adjust components to only have relevant schema
            swaggerSubset['components'] = {'schemas':{key:swagger['components']['schemas'][key] for key in swagger['components']['schemas'].keys() if idName in key}}
            # Add security components to the subset
            swaggerSubset['components']['securitySchemes'] = swagger['components']['securitySchemes']
            commonTypeList = irisDependencies[idName]
            commonTypeSchema = {commonTypeName:swagger['components']['schemas'][commonTypeName] for commonTypeName in commonTypeList}
            # update schema to contain common types written in dependencies
            ### COMMONTYPE SCHEMA WILL DOMINATE
            swaggerSubset['components']['schemas'].update(commonTypeSchema)
            # Save file based on folder specified
            with open(subsetPath+"/"+idName+".json",'w') as f:
                json.dump(swaggerSubset,f)
        return "SUCCESS"
    except Exception as e:
        print("Error duing saving")
        print(e)
        return "ERROR"
