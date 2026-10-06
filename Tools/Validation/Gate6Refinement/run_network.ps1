param([switch]$FinalCamera)
$ErrorActionPreference='Stop'
$taskRoot='D:\GitHub\RVSurvival\RVSurvival'
$taskCases=@(
 @{name='refine_client_baseline_repeat';driver='client';network=$false;disconnect=$true},
 @{name='refine_host_emulated';driver='host';network=$true;disconnect=$true},
 @{name='refine_client_emulated';driver='client';network=$true;disconnect=$true}
)
if($FinalCamera){$taskCases=@(@{name='refine_final_camera_client_emulated';driver='client';network=$true;disconnect=$true})}
foreach($taskCase in $taskCases){
 if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
 Get-ChildItem -LiteralPath ($taskRoot+'\Tools\Validation\Gate6Refinement') -Filter '*.py'|ForEach-Object{Copy-Item -LiteralPath $_.FullName -Destination ($taskRoot+'\Saved\Gate6Refinement\'+$_.Name)}
 $taskCase|ConvertTo-Json -Compress|Set-Content -LiteralPath ($taskRoot+'\Saved\Gate6Refinement\case.json')
 $taskStart=Get-Date;$taskQuote=[char]34
 $taskArgs=$taskQuote+$taskRoot+'\RVSurvival.uproject'+$taskQuote+' -ExecCmds='+$taskQuote+'py '+$taskRoot.Replace('\','/')+'/Saved/Gate6Refinement/launch_process.py'+$taskQuote+' -abslog='+$taskQuote+$taskRoot+'\Saved\Gate6Refinement\'+$taskCase.name+'.log'+$taskQuote
 $taskEditor=Start-Process 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
 if(-not $taskEditor.WaitForExit(360000)){throw ('Inspect timeout: '+$taskCase.name)}
 $taskPids=@()
 foreach($taskRole in @('server','client')){
  $taskFile=$taskRoot+'\Saved\Gate6Refinement\'+$taskCase.name+'_'+$taskRole+'.json'
  if(-not(Test-Path -LiteralPath $taskFile) -or (Get-Item -LiteralPath $taskFile).LastWriteTime -lt $taskStart){throw ('No fresh receipt: '+$taskFile)}
  $taskResult=Get-Content -LiteralPath $taskFile -Raw|ConvertFrom-Json;$taskPids+=$taskResult.pid
  $taskFailures=@($taskResult.results|Where-Object {-not $_.pass})
  Write-Output ($taskCase.name+' '+$taskRole+' checks='+$taskResult.results.Count+' failed='+$taskFailures.Count)
  if($taskFailures.Count){$taskFailures|ConvertTo-Json -Depth 8;throw ('Failed '+$taskCase.name)}
  $taskResult.PSObject.Properties.Remove('samples');$taskResult|ConvertTo-Json -Depth 20|Set-Content -LiteralPath ($taskRoot+'\Docs\Gate6Refinement\'+$taskCase.name+'_'+$taskRole+'.json')
 }
 if($taskPids[0] -eq $taskPids[1]){throw 'Expected separate process PIDs'}
 $taskErrors=Select-String -LiteralPath ($taskRoot+'\Saved\Gate6Refinement\'+$taskCase.name+'.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
 if($taskErrors){$taskErrors|Select-Object -Last 10;throw 'Editor errors'}
 $taskChildErrors=Select-String -LiteralPath ($taskRoot+'\Saved\Gate6Refinement\'+$taskCase.name+'_child.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
 if($taskChildErrors){$taskChildErrors|Select-Object -Last 10;throw 'Child process errors'}
}
