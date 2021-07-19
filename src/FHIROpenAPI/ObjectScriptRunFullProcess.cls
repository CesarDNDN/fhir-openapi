/// ObjectScript Class to run all processes in order
Class FHIROpenAPI.ObjectScriptRunFullProcess
{
    
    ClassMethod RunFHIRSwaggerCommand(errName) As %Status
    {
        set sc = $$$OK
        set serverPath = ^FHIRServerPath
        s savePath = $System.Util.ManagerDirectory()_"fhir-openapi\fhir-swagger\swagger.json"
        s tCommand = "fhir-swagger --fhir_url "_$C(34)_serverPath_$C(34)_" --conformance_path="_$C(34)_"/metadata?_format=application/json"_$C(34)_" --r4 --output "_savePath
        w tCommand, !
        s sc = $ZF(-100,"/SHELL/NOQUOTE/STDERR="_$C(34)_errName_$C(34),tCommand)
        s tSize = ##class(%File).GetFileSize(errName)
        return sc
    }

    ClassMethod RunMetadataRoutine() As %Status
    {
        set sc = $$$OK
        s ^OpenAPIBasePath = $System.Util.ManagerDirectory()_"fhir-openapi"
        do ^IRISFHIRMetadata
        return sc
    }

    ClassMethod RunPythonConversion(errName) As %Status
    {
        set sc = $$$OK
        s convertPath = ^OpenAPIBasePath_"\pyconvert\ConvertFile.py"
        s tCommand = "python3 "_convertPath
        w tCommand, !
        s sc = $ZF(-100,"/SHELL/NOQUOTE/STDERR="_$C(34)_errName_$C(34),tCommand)
        s tSize = ##class(%File).GetFileSize(errName)
        return sc
    }

    ClassMethod RunPythonAnnotation(errName) As %Status
    {
        set sc = $$$OK
        s convertPath = ^OpenAPIBasePath_"\pyannotate\AnnotateFiles.py"
        s tCommand = "python3 "_convertPath
        w tCommand, !
        s sc = $ZF(-100,"/SHELL/NOQUOTE/STDERR="_$C(34)_errName_$C(34),tCommand)
        s tSize = ##class(%File).GetFileSize(errName)
        return sc
    }

    ClassMethod RunPythonExemplify(errName) As %Status
    {
        set sc = $$$OK
        s convertPath = ^OpenAPIBasePath_"\pyexample\AddExamples.py"
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
        s sc = ..RunMetadataRoutine()
        s sc = ..RunPythonConversion(errName)
        s sc = ..RunPythonAnnotation(errName)
        s sc = ..RunPythonExemplify(errName)
        Return sc
    }
}