/// ObjectScript Class to run all processes in order
Class FHIROpenAPI.ObjectScriptRunFullProcess
{
    
    ClassMethod RunFHIRSwaggerCommand(errName) As %Status
    {
        /// Getting the Swagger Spec format for FHIR
        set sc = $$$OK
        set serverPath = ^FHIRServerPath
        s savePath = $System.Util.ManagerDirectory()_"fhir-openapi/fhir-swagger/swagger.json"
        s tCommand = "fhir-swagger --fhir_url "_$C(34)_serverPath_$C(34)_" --conformance_path="_$C(34)_"/metadata?_format=application/json"_$C(34)_" --r4 --output "_savePath
        w tCommand, !
        s sc = $ZF(-100,"/SHELL/NOQUOTE/STDERR="_$C(34)_errName_$C(34),tCommand)
        s tSize = ##class(%File).GetFileSize(errName)
        return sc
    }

    ClassMethod RunMetadataRoutine() As %Status
    {
        /// Getting the metadata for specified FHIR Package
        set sc = $$$OK
        do ^IRISFHIRMetadata
        w !, "SUCCESS", !
        return sc
    }

    ClassMethod RunPythonConversion(errName) As %Status
    {
        /// Convert Swagger 2.0 into OpenAPI 3.0
        set sc = $$$OK
        s convertPath = ^OpenAPIBasePath_"/pyconvert/ConvertFile.py"
        s tCommand = "python3 "_convertPath
        w tCommand, !
        s sc = $ZF(-100,"/SHELL/NOQUOTE/STDERR="_$C(34)_errName_$C(34),tCommand)
        s tSize = ##class(%File).GetFileSize(errName)
        return sc
    }

    ClassMethod RunPythonAnnotation(errName) As %Status
    {
        /// Annotate the OpenAPI 3.0 with FHIR Metadata
        set sc = $$$OK
        s convertPath = ^OpenAPIBasePath_"/pyannotate/AnnotateFiles.py"
        s tCommand = "python3 "_convertPath
        w tCommand, !
        s sc = $ZF(-100,"/SHELL/NOQUOTE/STDERR="_$C(34)_errName_$C(34),tCommand)
        s tSize = ##class(%File).GetFileSize(errName)
        return sc
    }

    ClassMethod RunPythonExemplify(errName) As %Status
    {
        /// Add the example formats for each resource
        set sc = $$$OK
        s convertPath = ^OpenAPIBasePath_"/pyexample/AddExamples.py"
        s tCommand = "python3 "_convertPath
        w tCommand, !
        s sc = $ZF(-100,"/SHELL/NOQUOTE/STDERR="_$C(34)_errName_$C(34),tCommand)
        s tSize = ##class(%File).GetFileSize(errName)
        return sc
    }

    

    /// Entire Process
    ClassMethod RunFullProcess() As %Status
    {
        Set sc = $$$OK
        s errName = ##class(%File).TempFilename("txt",,.sc)
        s sc = ..RunFHIRSwaggerCommand(errName)
        if (sc '= $$$OK && sc '= 0)
        {
            w "Error encountered. Error info recorded at "_errName
            return sc
        }
        s sc = ..RunMetadataRoutine()
        if (sc '= $$$OK)
        {
            w "Error encountered"
            return sc
        }
        s sc = ..RunPythonConversion(errName)
        if (sc '= $$$OK && sc '= 0)
        {
            w "Error encountered. Error info recorded at "_errName
            return sc
        }
        s sc = ..RunPythonAnnotation(errName)
        if (sc '= $$$OK && sc '= 0)
        {
            w "Error encountered. Error info recorded at "_errName
            return sc
        }
        s sc = ..RunPythonExemplify(errName)
        if (sc '= $$$OK && sc '= 0)
        {
            w "Error encountered. Error info recorded at "_errName
            return sc
        }
        w "Saving into Final Save Path... (Path: "_^FHIRSavePath_")",!

        s finalSave = ^FHIRSavePath_"/FHIRSpec.json"
        s ogSave = ^OpenAPIBasePath_"/output/openapi3.json"
        d ##class(%File).CopyFile(ogSave,finalSave,0,.sc)
        if (sc < 0)
        {
            w "Error encountered during saving."
            return sc
        }
        w "SUCCESS"
        Return sc
    }

    ClassMethod RunPreprocess() As %Status
    {
        /// Perform preprocessing step
        set sc = $$$OK  
        s done = 1
        while (done =1){
            s ^OpenAPIBasePath = $System.Util.ManagerDirectory()_"fhir-openapi"
            w "Please Input your Server Path as http://<path/to/your/FHIRServer>", !, "Ex: http://localhost:8000/r4",! ,"Below:",!
            r temppath
            w !, "Please Input your FHIRNamespace name Below:",! r tempnamespace
            w !,"Please Input your Metadata Spec Key",!,"Default is $lb(""hl7.fhir.r4.core@4.0.1"")",!,"Below:",!
            r tempspec
            if tempspec=""
            {
                s tempspec = $lb("hl7.fhir.r4.core@4.0.1")
            }
            w !,"Current parameters entered:",!,"Path:",temppath,!,"Spec Key:",tempspec,!,"Namespace:",tempnamespace,!
            w !,"Enter 0 if correct, 1 if need to retry",!
            r done
        }
        zn "HSLIB"
        do ##class(HS.HC.Util.Installer).InstallFoundation(tempnamespace)
        zn tempnamespace
        set schema = ##class(HS.FHIRServer.Schema).LoadSchema("HL7v40")
        s ^FHIRServerPath = temppath
        s ^OpenAPISpec = tempspec
        // Skipping SavePath configuration for now, the final save path is in the database.

        s ^FHIRSavePath = ^OpenAPIBasePath_"/output"
        return sc

    }
}