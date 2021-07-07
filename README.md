# IRIS FHIR OpenAPI Spec generator

Generator combines data from:
- FHIR server complience statement (/metadata resource)
- IRIS ^HS.FHIRServer.Meta
- Definitions and examples from https://hl7.org/FHIR/

And generates fully annotated OpenAPI v3 spec for all 133 resources and one "MEGASPEC", containing all resources and schemas.

There are four steps:
- Generate basic swagger2 spec, based on metadata (java code from 3rd party repo)
- Extract data from ^HS.FHIRServer.Meta global (object script)
- Convert Swagger2 to OpenAPI 3 spec (node.js)
- Annotate spec with data from hl7.org site, merge with data extracted from global, generate 133 resource-specific and 1 "megaspec" (node.js)
- add examples from hl4.org to resource - specific specs (node.js)

```bash
# FHIR Swagger
# https://github.com/rbren/fhir-swagger (see repo's README.md for instructions)
# Generates basic Swagger2 definition from FHIR server complience statement
# <server-url>/metadata
# !!! not in this repo
# source:
# - local IRIS instance
# targets:
# - ./fhir-swagger/iris-swagger.json
fhir-swagger \
--fhir_url "http://<your_base>/app/FHIR/r4" \
--conformance_path="/metadata?_format=application/json" \
--r4 \
--output ./fhir-swagger/iris-swagger.json

# Extract information from IRIS FHIR server metadata
# source:
# - ^HS.FHIRServer.Meta global
# targets:
# - ./fhir-swagger/iris-global.json
# - ./fhir-swagger/iris-dependencies.json
iris session iris
zn "FHIRNAMESPACE"
FHIRNAMESPACE>do ^IRISFHIRMetadata

# Convert swagger 2.0 to OpenAPI 3.0 spec
# Add content-type
# source:
# - ./fhir-swagger/iris-swagger.json
# target:
# - ./fhir-swagger/iris-openapi3.json
node convert.js

# annotate - enhance OpenAPI definitions with descriptions from hl7.org
# merge with data from ^HS.FHIR.Meta global
# add OAuth2 security
# sources:
# - ./fhir-swagger/iris-openapi3.json
# - ./fhir-swagger/iris-global.json
# - ./fhir-swagger/iris-dependencies.json
# - ./definitions.json/*.json - FHIR definitions from hl7.org
# targets:
# - ./output/swagger2.json "megaspec"
# - ./output/<resource name>.json 133 small, resource - specific specs
node annotate.js

# add payload examples to resource OpenAPI specs
# sources:
# - ./output/<resource name>.json
# - ./examples-json/*.json - FHIR examples from hl7.org
# targets:
# - ./output/<resource name>.json
node add-examples.js
```

Additional static files:

- ./output/index.html, ./output/swagger-ui.html - homepage for API browser
- ./output/oauth2-redirect.html static html, needed for OAuth2 authentication workflow
- ./output/ISC-FHIR-Icon.png ISC icon
