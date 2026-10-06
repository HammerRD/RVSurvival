$ErrorActionPreference='Stop'
$taskRoot='D:\GitHub\RVSurvival\RVSurvival'
$taskCases=@(@{name='refine_moving_host_baseline';driver='host';network=$false},@{name='refine_moving_client_emulated';driver='client';network=$true})
foreach($taskCase in $taskCases){
 if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
 $taskCase|ConvertTo-Json -Compress|Set-Content -LiteralPath ($taskRoot+'\Saved\Gate6RefinementMoving\moving_process_case.json')
 $taskStart=Get-Date;$taskQuote=[char]34
 $taskArgs=$taskQuote+$taskRoot+'\RVSurvival.uproject'+$taskQuote+' -ExecCmds='+$taskQuote+'py '+$taskRoot.Replace('\','/')+'/Saved/Gate6RefinementMoving/run_moving.py'+$taskQuote+' -abslog='+$taskQuote+$taskRoot+'\Saved\Gate6RefinementMoving\'+$taskCase.name+'.log'+$taskQuote
 Write-Output ('START '+$taskCase.name)
 $taskEditor=Start-Process 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $taskArgs -WindowStyle Hidden -PassThru
 if(-not $taskEditor.WaitForExit(420000)){throw ('Inspect timeout '+$taskCase.name)}
 foreach($taskRole in @('server','client')){
  $taskFile=$taskRoot+'\Saved\Gate6RefinementMoving\'+$taskCase.name+'_'+$taskRole+'.json'
  if(-not(Test-Path -LiteralPath $taskFile) -or (Get-Item -LiteralPath $taskFile).LastWriteTime -lt $taskStart){throw ('Missing fresh receipt '+$taskFile)}
  $taskResult=Get-Content -LiteralPath $taskFile -Raw|ConvertFrom-Json;$taskFails=@($taskResult.results|Where-Object {-not $_.pass})
  Write-Output ($taskCase.name+' '+$taskRole+' checks='+$taskResult.results.Count+' failed='+$taskFails.Count)
  if($taskFails.Count){$taskFails|ConvertTo-Json -Depth 8;throw ('Moving regression failed '+$taskCase.name)}
  $taskResult.PSObject.Properties.Remove('samples');$taskResult|ConvertTo-Json -Depth 25|Set-Content -LiteralPath ($taskRoot+'\Docs\Gate6Refinement\'+$taskCase.name+'_'+$taskRole+'.json')
 }
 foreach($taskSuffix in @('.log','_child.log')){
  $taskErrors=Select-String -LiteralPath ($taskRoot+'\Saved\Gate6RefinementMoving\'+$taskCase.name+$taskSuffix) -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
  if($taskErrors){$taskErrors|Select-Object -Last 10;throw 'Editor/client errors'}
 }
 & 'D:/Epic Games/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' ($taskRoot+'\Saved\Gate6RefinementMoving\compare.py') $taskCase.name
 if($LASTEXITCODE -ne 0){throw 'Paired moving comparison failed'}
}
