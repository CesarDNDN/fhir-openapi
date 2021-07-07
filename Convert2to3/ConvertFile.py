import ConvertFileUtils
import json

def ConvertMain(filepath,savepath):
    with open(filepath,'r') as f:
        source = json.load(f)
    target = ConvertFileUtils.configureNewSwagger(source)
    target = ConvertFileUtils.moveParameters(target)
    target = ConvertFileUtils.moveVerbTypes(target)
    target = ConvertFileUtils.addRequestBody(target)
    target = ConvertFileUtils.addResponseBody(target)
    print("Successful Conversion. Saving new file...")
    with open(savepath,'w') as f:
        json.dump(target,f)
    
if __name__ == "__main__":
    ConvertMain('./fhir-swagger/iris-swagger.json', './fhir-swagger/iris-openapi3.json')