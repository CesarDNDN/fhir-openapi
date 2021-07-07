import unittest
import ConvertFileUtils
import json

class BasicTest(unittest.TestCase):
    
    def testBegin(self):
        self.assertTrue(True)

    def testInitial(self):
        # Tests the initialization of the conversion
        with open('Convert2to3/Patient.json','r') as f:
            source = json.load(f)
        target = ConvertFileUtils.configureNewSwagger(source)

        # Assert the target is dictionary type
        self.assertIsInstance(target,dict)
        #Assert swagger was removed from keys
        self.assertFalse('swagger' in target.keys())
        #Assert openapi key exists
        self.assertTrue('openapi' in target.keys())
        #Assert server url moved correctly
        self.assertFalse('schemes' in target.keys())
        self.assertFalse('host' in target.keys())
        self.assertFalse('basePath' in target.keys())
        self.assertTrue('url' in target['servers'][0])
        self.assertEqual(target['servers'][0]['url'],source['schemes'][0]+'://'+source['host']+source['basePath'])
        #Assert the definitions moved into schemas
        self.assertEqual(target['components']['schemas'],source['definitions'])

    def testParameters(self):
        # tests that the parameter types were correctly moved to the schema key
        with open('Convert2to3/Patient.json','r') as f:
            source = json.load(f)
        target = ConvertFileUtils.configureNewSwagger(source)
        target = ConvertFileUtils.moveParameters(target)
        #Assert type was correctly moved
        self.assertFalse('type' in target['paths']['/Patient/{id}']['parameters'][0])
        self.assertEqual(target['paths']['/Patient/{id}']['parameters'][0]['schema']['type'],source['paths']['/Patient/{id}']['parameters'][0]['type'])
        
        #Assert rest of file paths remains unchanged besides parameters
        target['paths']['/Patient/{id}'].pop('parameters')
        source['paths']['/Patient/{id}'].pop('parameters')
        self.assertEqual(source['paths'],target['paths'])

    def testVerbs(self):
        #tests that the verb types were shifted correctly
        with open('Convert2to3/Patient.json','r') as f:
            source = json.load(f)
        target = ConvertFileUtils.configureNewSwagger(source)
        target = ConvertFileUtils.moveParameters(target)
        target = ConvertFileUtils.moveVerbTypes(target)
        self.assertFalse('type' in target['paths']['/Patient']['get']['parameters'][0])
        self.assertEqual(target['paths']['/Patient']['get']['parameters'][0]['schema']['type'],source['paths']['/Patient']['get']['parameters'][0]['type'])
        self.assertEqual(target['paths']['/Patient']['get']['parameters'][8]['schema']['format'],source['paths']['/Patient']['get']['parameters'][8]['format'])

    def testRequestBody(self):
        #tests that the requestBody was added and parameters was removed from put post
        with open('Convert2to3/Patient.json','r') as f:
            source = json.load(f)
        target = ConvertFileUtils.configureNewSwagger(source)
        target = ConvertFileUtils.moveParameters(target)
        target = ConvertFileUtils.moveVerbTypes(target)
        target = ConvertFileUtils.addRequestBody(target)
        self.assertFalse('parameters' in target['paths']['/Patient']['post'].keys())
        self.assertFalse('consumes' in target['paths']['/Patient']['post'].keys())
        self.assertTrue('requestBody' in target['paths']['/Patient']['post'].keys())

    def testResponseBody(self):
        #tests that the responseBody was added and schema was removed from responses
        with open('Convert2to3/Patient.json','r') as f:
            source = json.load(f)
        target = ConvertFileUtils.configureNewSwagger(source)
        target = ConvertFileUtils.moveParameters(target)
        target = ConvertFileUtils.moveVerbTypes(target)
        target = ConvertFileUtils.addRequestBody(target)
        target = ConvertFileUtils.addResponseBody(target)
        self.assertFalse('schema' in target['paths']['/Patient/{id}/_history/{vid}']['get']['responses']['200'].keys())
        self.assertTrue('content' in target['paths']['/Patient/{id}/_history/{vid}']['get']['responses']['200'].keys())
        

if __name__ == '__main__':
    unittest.main()
