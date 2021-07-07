import json
import AddExampleUtils

def AddExampleMain():
    dirName = './examples-json'
    with open('./output/openapi3.json',encoding='utf8') as f:
        swagger = json.load(f)
    fileList = AddExampleUtils.getFileList(dirName)
    examplesDict = AddExampleUtils.getSwaggerExamples(swagger,fileList)
    print("Saving examples...")
    status = AddExampleUtils.updateResourceJsons(swagger,examplesDict,dirName)
    print(status)

if __name__ == "__main__":
    AddExampleMain()