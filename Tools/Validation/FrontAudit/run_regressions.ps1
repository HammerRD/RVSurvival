$ErrorActionPreference='Stop'
$taskRoot='D:\GitHub\RVSurvival\RVSurvival'
$engine='D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$python='D:\Epic Games\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
$cases=@(
 @{name='front_followup_seats';network=$false;kind='process'},
 @{name='front_followup_host';driver='host';network=$false;kind='moving'},
 @{name='front_followup_client';driver='client';network=$false;kind='moving'}
)
foreach($case in $cases){
 $config=if($case.kind -eq 'moving'){'moving_process_case.json'}else{'case.json'}
 $runner=if($case.kind -eq 'moving'){'run_moving.py'}else{'run_process.py'}
 $case|ConvertTo-Json -Compress|Set-Content -LiteralPath ($taskRoot+'\Saved\Gate5Refinement\'+$config)
 $started=Get-Date
 Write-Output ('START '+$case.name)
 $q=[char]34
 $args=$q+$taskRoot+'\RVSurvival.uproject'+$q+' -ExecCmds='+$q+'py '+$taskRoot.Replace('\','/')+'/Saved/Gate5Refinement/'+$runner+$q+' -abslog='+$q+$taskRoot+'\Saved\Gate5Refinement\'+$case.name+'.log'+$q
 $job=Start-Process -FilePath $engine -ArgumentList $args -WindowStyle Hidden -PassThru
 if(-not $job.WaitForExit(420000)){throw ('Editor timeout: '+$case.name)}
 foreach($role in @('server','client')){
  $file=$taskRoot+'\Saved\Gate5Refinement\'+$case.name+'_'+$role+'.json'
  if(-not(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).LastWriteTime -lt $started){throw ('Fresh receipt missing '+$file)}
  $data=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json
  $failed=@($data.results|Where-Object {-not $_.pass})
  Write-Output ($case.name+' '+$role+' checks='+@($data.results).Count+' failures='+$failed.Count)
  if($failed.Count){$failed|ConvertTo-Json -Depth 6;throw ('Failed case '+$case.name)}
  $data.PSObject.Properties.Remove('samples')
  $data|ConvertTo-Json -Depth 25|Set-Content -LiteralPath ($taskRoot+'\Docs\Gate5Refinement\'+$case.name+'_'+$role+'.json')
 }
 $errors=Select-String -LiteralPath ($taskRoot+'\Saved\Gate5Refinement\'+$case.name+'.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
 if($errors){$errors|Select-Object -Last 10;throw ('Editor errors '+$case.name)}
 if($case.kind -eq 'moving'){
  & $python ($taskRoot+'\Saved\Gate5Refinement\compare_moving.py') $case.name
  if($LASTEXITCODE -ne 0){throw ('Paired comparison failed '+$case.name)}
 }
 Write-Output ('COMPLETE '+$case.name)
}
