
s pNamespace="FHIRSERVER"
ZN "HSLIB"
Do ##class(HS.HC.Util.Installer).InstallFoundation(pNamespace)
Do ##class(HS.FHIRServer.Installer).InstallNamespace(pNamespace)
ZN pNamespace


Set tFHIRApp = "/csp/healthshare/fhirserver/fhir/r4"
Set tStrategyClass = "HS.FHIRServer.Storage.Json.InteractionsStrategy"
Set tMetadataConfigKey = "HL7v40"
Do ##class(HS.FHIRServer.Installer).InstallInstance(tFHIRApp, tStrategyClass, tMetadataConfigKey,"",0)

Set strategy = ##class(HS.FHIRServer.API.InteractionsStrategy).GetStrategyForEndpoint(tFHIRApp) 
Set configData = strategy.GetServiceConfigData() 
Set configData.DebugMode = 4
Do strategy.SaveServiceConfigData(configData)
