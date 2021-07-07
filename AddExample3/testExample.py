import unittest
import os
import AddExampleUtils
import json

class BasicTest(unittest.TestCase):
    
    def testBegin(self):
        self.assertTrue(True)

    def testFileList(self):
        # Test whether all the files were correctly added
        fileList = AddExampleUtils.getFileList('./examples-json')
        self.assertTrue('account-example.json' in fileList)

    def testSwaggerExamples(self):
        # Test whether the files were filtered by example
        with open('./fhir-swagger/iris-openapi3.json',encoding='utf8') as f:
            swagger = json.load(f)
        fileList = AddExampleUtils.getFileList('./examples-json')
        examplesDict = AddExampleUtils.getSwaggerExamples(swagger,fileList)
        # Test to check validity of keys
        self.assertTrue('Account' in examplesDict.keys())
        # Test to verify non-example files added to the dictionary
        self.assertFalse('account.profile.json' in examplesDict['Account'])

    def testUpdateFiles(self):
        # Test whether the files were saved successfully
        dirName = './examples-json'
        with open('./fhir-swagger/iris-openapi3.json',encoding='utf8') as f:
            swagger = json.load(f)
        fileList = AddExampleUtils.getFileList(dirName)
        examplesDict = AddExampleUtils.getSwaggerExamples(swagger,fileList)
        status = AddExampleUtils.updateResourceJsons(swagger,examplesDict,dirName)
        # Test to verify save status
        self.assertEqual(status,"SUCCESS")

if __name__ == '__main__':
    unittest.main()
