import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import ConvertFileUtils

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
    print("SUCCESS")
    
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ConvertMain('./fhir-swagger/swagger.json', './fhir-swagger/iris-openapi3.json')