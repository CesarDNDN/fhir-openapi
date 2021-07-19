import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import AddExampleUtils

def AddExampleMain():
    dirName = './examples'
    with open('./output/openapi3.json',encoding='utf8') as f:
        swagger = json.load(f)
    fileList = AddExampleUtils.getFileList(dirName)
    examplesDict = AddExampleUtils.getSwaggerExamples(swagger,fileList)
    print("Saving examples...")
    status = AddExampleUtils.updateResourceJsons(swagger,examplesDict,dirName)
    print(status)
    # workspace_name = os.listdir('./workspaces')[0]
    # print("Finalizing saving OpenAPI Spec to "+workspace_name+" workspace")
    # json.dump(json.load(open('./output/openapi3.json',encoding='utf8')),open('./workspaces/'+workspace_name+'/specs/openapi3.json','w',encoding='utf8'))
    # print("SUCCESS")
    return "SUCCESS"

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    AddExampleMain()