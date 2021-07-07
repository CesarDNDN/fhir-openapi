import unittest
import os
import AnnotateFileUtils
import json

class BasicTest(unittest.TestCase):
    
    def testBegin(self):
        self.assertTrue(True)

    def testParamDescFunc(self):
        # Test Search Params description function from Utils
        with open('./definitions.json/search-parameters.json',encoding='utf8') as f:
            searchParams = json.load(f)
        # Case with multiple resources
        description = AnnotateFileUtils.getParamDesc(searchParams,'patient','birthdate')
        self.assertEqual(description,"The patient's date of birth")
        # Case with single resource
        description = AnnotateFileUtils.getParamDesc(searchParams,'/patient','deceased')
        self.assertEqual('This patient has been marked as deceased, or as a death date entered',description)
        # Case with invalid resource (deceased1)
        description = AnnotateFileUtils.getParamDesc(searchParams,'/patient','deceased1')
        self.assertEqual('UNABLE TO FIND',description)

    def testElementDescFunc(self):
        #Test Data Element description function from Utils
        with open('./definitions.json/dataelements.json',encoding='utf8') as f:
            dataElements = json.load(f)
        # Test Case 1 on birthdate description
        description = AnnotateFileUtils.getElementDesc(dataElements,'patient','birthdate')
        #Test Case 2 on Gender description
        self.assertEqual(description,"The date of birth for the individual")
        description = AnnotateFileUtils.getElementDesc(dataElements,'patient','Gender')
        self.assertEqual(description,"male | female | other | unknown")
        #Test Case with invalid element (gender1)
        description = AnnotateFileUtils.getElementDesc(dataElements,'patient','gender1')
        self.assertEqual(description,"UNABLE TO FIND RESOURCE NAME")
    
    def testProfileDescFunc(self):
        # Test Profile Resources description function from Utils
        with open('./definitions.json/profiles-resources.json',encoding='utf8') as f:
            profileResources = json.load(f)
        # Test Case with patient
        description = AnnotateFileUtils.getProfileDesc(profileResources,'patient')
        self.assertEqual(description,"Information about an individual or animal receiving health care services")
        # Test Case with invalid resource (patient1)
        description = AnnotateFileUtils.getProfileDesc(profileResources,'patient1')
        self.assertEqual(description,"UNABLE TO FIND RESOURCE NAME")
        
    def testProfileElementDescFunc(self):
        # Test Profile Resources on Elements description function from Utils
        with open('./definitions.json/profiles-resources.json',encoding='utf8') as f:
            profileResources = json.load(f)
        # Test Case with patient and Gender
        description = AnnotateFileUtils.getProfileElementDesc(profileResources,'patient','Gender')
        self.assertEqual(description,"male | female | other | unknown")
        # Invalid Test Case (gender1)
        description = AnnotateFileUtils.getProfileElementDesc(profileResources,'patient','gender1')
        self.assertEqual(description,"UNABLE TO FIND RESOURCE/ELEMENT NAME")

    def testSetSwaggerParams(self):
        # Test setting swagger parameter based on the search parameters
        with open('./definitions.json/search-parameters.json',encoding='utf8') as f:
            searchParams = json.load(f)
        with open('./fhir-swagger/iris-openapi3.json',encoding='utf8') as f:
            swagger = json.load(f)
        swagger = AnnotateFileUtils.setSwaggerParamDesc(swagger,searchParams)
        # Test Case with Supply Request
        self.assertEqual(swagger['paths']['/SupplyRequest']['get']['parameters'][0]['description'],'product-problem | product-quality | product-use-error | wrong-dose | incorrect-prescribing-information | wrong-technique | wrong-route-of-administration | wrong-rate | wrong-duration | wrong-time | expired-drug | medical-device-use-error | problem-different-manufacturer | unsafe-physical-environment')

    def testSetDefinitions(self):
        # Test setting the swagger components to the definitions written from metadata
        with open('./fhir-swagger/iris-global.json',encoding='utf8') as f:
            irisDefs = json.load(f)
        with open('./fhir-swagger/iris-openapi3.json',encoding='utf8') as f:
            swagger = json.load(f)
        swagger = AnnotateFileUtils.setIrisDefinitions(swagger,irisDefs)
        # Verifying that schemas is the only key in components
        self.assertEqual(len(swagger['components'].keys()),1)
        # Verifying that the schemas key was set to the IRIS Definitions found earlier
        self.assertEqual(swagger['components']['schemas'],irisDefs)


    def testSetSchemas(self):
        # Test setting the swagger component schema definitions to what is present in the profile resources/data elements
        with open('./fhir-swagger/iris-dependencies.json',encoding='utf8') as f:
            irisDeps = json.load(f)
        with open('./fhir-swagger/iris-openapi3.json',encoding='utf8') as f:
            swagger = json.load(f)
        with open('./definitions.json/profiles-resources.json',encoding='utf8') as f:
            profileResources = json.load(f)
        with open('./definitions.json/dataelements.json',encoding='utf8') as f:
            dataElements = json.load(f)
        with open('./fhir-swagger/iris-global.json',encoding='utf8') as f:
            irisDefs = json.load(f)
        swagger = AnnotateFileUtils.setIrisDefinitions(swagger,irisDefs)
        swagger = AnnotateFileUtils.setSchemas(swagger,irisDeps,profileResources,dataElements)
        # Test to check a property definition set correctly
        self.assertEqual(swagger['components']['schemas']['VisionPrescription']['properties']['contained']['description'],"Contained, inline Resources")
        # Test to cehck a resource definition set correctly
        self.assertEqual(swagger['components']['schemas']['ActivityDefinition']['description'],'The definition of a specific activity to be taken, independent of any particular patient or context')
        

    def testSetSecurity(self):
        # Test setting the security oauth2 to template necessary for authentication
        with open('./fhir-swagger/iris-openapi3.json') as f:
            swagger = json.load(f)
        swagger = AnnotateFileUtils.setSecurity(swagger)
        # Test to verify there are security schemes in place
        self.assertEqual(list(swagger['components']['securitySchemes'].keys())[0],"oauth2")
        # Test to verify that a random command received the correct auth codes
        self.assertEqual(swagger['paths']['/TerminologyCapabilities']['get']['security'][0]['oauth2'][0],'user/*.write')

    def testSaveSwagger(self):
        # Test saving the swagger
        with open('./fhir-swagger/iris-openapi3.json') as f:
            swagger = json.load(f)
        with open('./definitions.json/profiles-resources.json',encoding='utf8') as f:
            profileResources = json.load(f)
        with open('./fhir-swagger/iris-dependencies.json',encoding='utf8') as f:
            irisDeps = json.load(f)
        with open('./definitions.json/dataelements.json',encoding='utf8') as f:
            dataElements = json.load(f)
        with open('./fhir-swagger/iris-global.json',encoding='utf8') as f:
            irisDefs = json.load(f)
        # Run entire process first
        swagger = AnnotateFileUtils.setIrisDefinitions(swagger,irisDefs)
        swagger = AnnotateFileUtils.setSchemas(swagger,irisDeps,profileResources,dataElements)
        swagger = AnnotateFileUtils.setSecurity(swagger)
        status = AnnotateFileUtils.saveSwagger(swagger,'./output/pythonswagger.json','./output',profileResources,irisDeps)
        # Test to see if save was successful, any error caught will be caught in the save function and return 'ERROR'
        self.assertEqual(status,"SUCCESS")

if __name__ == '__main__':
    unittest.main()
