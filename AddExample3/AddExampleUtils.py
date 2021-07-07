import os
import json

def getFileList(dirName):
    """
    Get the file names in the examples directory
    """
    fileList = [fileName for fileName in os.listdir(dirName) if os.path.isfile(dirName+"/"+fileName)]
    return fileList


def getSwaggerExamples(swagger,fileList):
    """
    Filter the extraneous files out that aren't examples
    Create a dictionary to store the examples keyed by their resource name
    """
    examplesDict = {}
    for id in range(len(swagger['tags'])):
        # Get resource name for pattern matching
        resourceName = swagger['tags'][id]['name']
        fileListFiltered = [fileName for fileName in fileList if fileName[:len(resourceName)+8].lower()==resourceName.lower()+"-example"]
        # Add the filtered version of the examples to our dictionary keyed by the resource name
        examplesDict[resourceName] = fileListFiltered
    return examplesDict

def updateResourceJsons(swagger,examplesDict,dirName):
    """
    Update the Resource JSON file to include examples in other folder
    """
    try:
        # Iterate through all resources in the output folder
        for id in range(len(swagger['tags'])):
            resourceName = swagger['tags'][id]['name']
            if resourceName == 'CapabilityStatement':
                continue
            # create swagger subset which was initially created in 'AnnotateFiles.py'
            with open('./output/'+resourceName+'.json',encoding='utf8') as f:
                swaggerSubset = json.load(f)
            resourceExamples = {}
            # Iterate through all examples for the resource
            for example in examplesDict[resourceName]:
                with open(dirName+"/"+example,encoding='utf8') as f:
                    exampleContents = json.load(f)
                # Add the example keyed by the file name
                resourceExamples[example] = {"value":exampleContents}
            swaggerSubset['paths']['/'+resourceName]['post']['requestBody']['content']['application/fhir+json']['examples'] = resourceExamples
            swagger['paths']['/'+resourceName]['post']['requestBody']['content']['application/fhir+json']['examples'] = resourceExamples
            # Save the file with 'w' to overwrite current outputted file
            with open('./output/'+resourceName+'.json','w',encoding='utf8') as f:
                json.dump(swaggerSubset,f)
        # Return status
        with open('./output/openapi3.json','w',encoding='utf8') as f:
            json.dump(swagger,f)
        return "SUCCESS"
    except Exception as e:
        print("Error duing saving")
        print(e)
        return "ERROR"
