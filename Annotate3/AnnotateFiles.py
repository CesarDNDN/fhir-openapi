import AnnotateFileUtils
import json

def AnnotateMain():
    with open('./definitions.json/search-parameters.json',encoding='utf8') as f:
        searchParams = json.load(f)
    with open('./definitions.json/dataelements.json',encoding='utf8') as f:
        dataElements = json.load(f)
    with open('./definitions.json/profiles-resources.json',encoding='utf8') as f:
        profileResources = json.load(f)
    with open('./fhir-swagger/iris-openapi3.json',encoding='utf8') as f:
        swagger = json.load(f)
    swagger = AnnotateFileUtils.setSwaggerParamDesc(swagger,searchParams)
    with open('./fhir-swagger/iris-global.json',encoding='utf8') as f:
        irisDefinitions = json.load(f)
    with open('./fhir-swagger/iris-dependencies.json',encoding='utf8') as f:
        irisDependencies = json.load(f)
    swagger = AnnotateFileUtils.setIrisDefinitions(swagger,irisDefinitions)
    swagger = AnnotateFileUtils.setSchemas(swagger,irisDependencies,profileResources,dataElements)
    swagger = AnnotateFileUtils.setSecurity(swagger)
    print("Successful Annotation. Saving new files...")
    status = AnnotateFileUtils.saveSwagger(swagger,'./output/openapi3.json','./output',profileResources,irisDependencies)
    print(status)

if __name__ == "__main__":
    AnnotateMain()