$ErrorActionPreference='Stop'
$taskRoot='D:\GitHub\RVSurvival\RVSurvival'
$taskEngine='D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$taskPython='D:\Epic Games\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
$taskCases=@(
 @{name='survival_baseline';network=$false;type='survival'},
 @{name='survival_emulated';network=$true;type='survival'},
 @{name='moving_host_baseline';driver='host';network=$false;type='moving'},
 @{name='moving_client_baseline';driver='client';network=$false;type='moving'},
 @{name='moving_host_emulated';driver='host';network=$true;type='moving'},
 @{name='moving_client_emulated';driver='client';network=$true;type='moving'}
)
foreach($taskCase in $taskCases) {
 $taskConfig=if($taskCase.type -eq 'moving'){'moving_process_case.json'}else{'survival_process_case.json'}
 $taskRunner=if($taskCase.type -eq 'moving'){'run_process_moving.py'}else{'run_process.py'}
 $taskCase | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $taskRoot ('Saved\Gate5Validation\'+$taskConfig))
 $taskStarted=Get-Date
 Write-Output ('START '+$taskCase.name)
 $taskProcess=Start-Process -FilePath $taskEngine -ArgumentList ('"'+$taskRoot+'\RVSurvival.uproject"'),('-ExecCmds="py '+($taskRoot.Replace('\','/'))+'/Saved/Gate5Validation/'+$taskRunner+'"') -WindowStyle Hidden -PassThru
 if(-not $taskProcess.WaitForExit(400000)){throw ('Editor timeout '+$taskCase.name+' PID '+$taskProcess.Id+'; inspect before any cleanup')}
 Start-Sleep -Seconds 2
 foreach($taskRole in @('server','client')) {
  $taskReceipt=Join-Path $taskRoot ('Saved\Gate5Validation\'+$taskCase.name+'_'+$taskRole+'.json')
  if(-not(Test-Path -LiteralPath $taskReceipt) -or (Get-Item -LiteralPath $taskReceipt).LastWriteTime -lt $taskStarted){throw ('Missing fresh receipt '+$taskReceipt)}
  $taskData=Get-Content -LiteralPath $taskReceipt -Raw | ConvertFrom-Json
  $taskFailed=@($taskData.results | Where-Object {-not $_.pass})
  Write-Output ($taskRole+' checks='+@($taskData.results).Count+' failed='+$taskFailed.Count)
  if($taskFailed.Count){$taskFailed | ConvertTo-Json -Depth 8;throw ('Failed '+$taskCase.name)}
  $taskData.PSObject.Properties.Remove('samples')
  $taskData | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $taskRoot ('Docs\Gate5Results\'+$taskCase.name+'_'+$taskRole+'.json'))
 }
 foreach($taskLog in @('RVSurvival.log','RVSurvival_2.log')) {
  $taskLogPath=Join-Path $taskRoot ('Saved\Logs\'+$taskLog)
  if(Test-Path -LiteralPath $taskLogPath){Copy-Item -LiteralPath $taskLogPath -Destination (Join-Path $taskRoot ('Saved\Gate5Validation\'+$taskCase.name+'_'+$taskLog))}
  $taskErrors=Select-String -LiteralPath $taskLogPath -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
  if($taskErrors){$taskErrors | Select-Object -Last 8;throw ('Automation/runtime error '+$taskCase.name)}
 }
 if($taskCase.type -eq 'moving') {& $taskPython (Join-Path $taskRoot 'Tools\Validation\gate5_compare_moving.py') $taskCase.name}
 else {& $taskPython (Join-Path $taskRoot 'Saved\Gate5Validation\compare_survival_generic.py') $taskCase.name}
 if($LASTEXITCODE -ne 0){throw ('Paired comparison failed '+$taskCase.name)}
 Write-Output ('COMPLETE '+$taskCase.name)
}
