$ErrorActionPreference='Stop'
$taskRoot='D:\GitHub\RVSurvival\RVSurvival'
$taskEngine='D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$taskCases=@(
 @{name='single_final';runner='run_single.py';receipt='Saved\Gate5Validation\single.json';kind='rows'},
 @{name='gate1_regression';runner='run_gate1_final.py';receipt='Docs\Gate5Results\Gate1Regression\summary.json';kind='summary'},
 @{name='gate2_regression';runner='run_gate2_final.py';receipt='Docs\Gate5Results\Gate2Regression\shared.json';kind='array'},
 @{name='gate4_regression';runner='run_inventory_regression.py';receipt='Saved\Gate5Validation\full.json';kind='rows'},
 @{name='stress_final';runner='run_stress.py';receipt='Saved\Gate5Validation\stress.json';kind='rows'}
)
foreach($taskCase in $taskCases) {
 $taskStarted=Get-Date
 Write-Output ('START '+$taskCase.name)
 $taskProcess=Start-Process -FilePath $taskEngine -ArgumentList ('"'+$taskRoot+'\RVSurvival.uproject"'),('-ExecCmds="py '+($taskRoot.Replace('\','/'))+'/Saved/Gate5Validation/'+$taskCase.runner+'"') -WindowStyle Hidden -PassThru
 if(-not $taskProcess.WaitForExit(300000)){throw ('Editor timeout '+$taskCase.name+' PID '+$taskProcess.Id)}
 Start-Sleep -Seconds 2
 $taskReceipt=Join-Path $taskRoot $taskCase.receipt
 if(-not(Test-Path -LiteralPath $taskReceipt) -or (Get-Item -LiteralPath $taskReceipt).LastWriteTime -lt $taskStarted){throw ('Missing fresh receipt '+$taskReceipt)}
 $taskData=Get-Content -LiteralPath $taskReceipt -Raw | ConvertFrom-Json
 if($taskCase.kind -eq 'summary'){if(-not $taskData.pass){throw ('Failed '+$taskCase.name)};Write-Output ('checks='+$taskData.checks)}
 else {
  $taskRows=if($taskCase.kind -eq 'array'){$taskData}else{$taskData.results}
  $taskFailed=@($taskRows | Where-Object {-not $_.pass})
  Write-Output ('checks='+@($taskRows).Count+' failed='+$taskFailed.Count)
  if($taskFailed.Count){$taskFailed | ConvertTo-Json -Depth 8;throw ('Failed '+$taskCase.name)}
 }
 if($taskCase.name -eq 'gate2_regression') {
  $taskExtra=Get-Content -LiteralPath (Join-Path $taskRoot 'Docs\Gate5Results\Gate2Regression\inventory-possession.json') -Raw | ConvertFrom-Json
  if(@($taskExtra | Where-Object {-not $_.pass}).Count){throw 'Inventory possession regression failed'}
  Write-Output ('possession checks='+@($taskExtra).Count)
 }
 foreach($taskLog in @('RVSurvival.log')) {
  $taskLogPath=Join-Path $taskRoot ('Saved\Logs\'+$taskLog)
  Copy-Item -LiteralPath $taskLogPath -Destination (Join-Path $taskRoot ('Saved\Gate5Validation\'+$taskCase.name+'_'+$taskLog))
  $taskErrors=Select-String -LiteralPath $taskLogPath -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
  if($taskErrors){$taskErrors | Select-Object -Last 8;throw ('Automation/runtime error '+$taskCase.name)}
 }
 $taskData | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $taskRoot ('Docs\Gate5Results\'+$taskCase.name+'.json'))
 Write-Output ('COMPLETE '+$taskCase.name)
}
