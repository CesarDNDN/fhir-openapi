/// Description
Class FHIROpenAPI.Generator Extends FHIROpenAPI.ObjectScriptRunFullProcess
{
    /// Preprocess
    ClassMethod Preprocess() As %Status
    {
        set sc = ..RunPreprocess()
        return sc
    }

    /// Process
    ClassMethod Run() As %Status
    {
        Set sc = ..RunFullProcess()
        // do something
        Return sc
    }
}