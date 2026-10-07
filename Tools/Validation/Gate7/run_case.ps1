param([Parameter(Mandatory)][string]$Name,[Parameter(Mandatory)][string]$Runner,[Parameter(Mandatory)][string]$Receipt)
$ErrorActionPreference='Stop'
$root='D:/GitHub/RVSurvival/RVSurvival';$base=$root+'/Saved/Gate7Validation/'
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
$started=Get-Date
if(Test-Path ($base+$Name+'.log')){Copy-Item ($base+$Name+'.log') ($base+'History/'+$Name+'-'+(Get-Date -Format yyyyMMddHHmmss)+'.log')}
$args='"'+$root+'/RVSurvival.uproject" -ExecCmds="py '+$root+'/'+$Runner+'" -abslog="'+$base+$Name+'.log"'
$job=Start-Process 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $args -WindowStyle Hidden -PassThru
while(!$job.HasExited){Start-Sleep -Seconds 2;if((Get-Date)-$started -gt [TimeSpan]::FromMinutes(7)){throw 'Inspect timeout; do not force kill'}}
$job.Dispose();Start-Sleep -Seconds 1
$path=$root+'/'+$Receipt
if(!(Test-Path $path) -or (Get-Item $path).LastWriteTime -lt $started){throw 'Missing fresh receipt'}
& 'D:/Epic Games/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' ($root+'/Tools/Validation/Gate7/Regressions/validate_receipt.py') $path
if($LASTEXITCODE -ne 0){throw 'Failed checks; inspect preserved receipt'}
if(Select-String -Path ($base+$Name+'.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'){throw 'Editor errors'}
$result=Get-Content $path -Raw|ConvertFrom-Json
if($result.samples){$result|Add-Member -NotePropertyName sample_count -NotePropertyValue $result.samples.Count;$result.PSObject.Properties.Remove('samples')}
$result|ConvertTo-Json -Depth 30|Set-Content ($root+'/Docs/Gate7Results/'+$Name+'.json') -Encoding utf8
Write-Output ('PASS '+$Name)
