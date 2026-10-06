$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$engine='D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$python='D:\Epic Games\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
$cases=@(
 @{name='moving_root_client_emulated';kind='moving';driver='client';network=$true}
)
foreach($case in $cases){
 if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
 $moving=$case.kind -eq 'moving'
 $config=if($moving){'moving_process_case.json'}else{'case.json'}
 $runner=if($moving){'run_moving.py'}else{'launch_process.py'}
 $case|ConvertTo-Json -Compress|Set-Content -LiteralPath ($root+'\Saved\Gate6Validation\'+$config)
 Write-Output ('START '+$case.name)
 $start=Get-Date;$q=[char]34
 $args=$q+$root+'\RVSurvival.uproject'+$q+' -ExecCmds='+$q+'py '+$root.Replace('\','/')+'/Saved/Gate6Validation/'+$runner+$q+' -abslog='+$q+$root+'\Saved\Gate6Validation\'+$case.name+'.log'+$q
 $job=Start-Process -FilePath $engine -ArgumentList $args -WindowStyle Hidden -PassThru
 if(-not $job.WaitForExit(420000)){throw ('Editor timeout '+$case.name)}
 foreach($role in @('server','client')){
  $file=$root+'\Saved\Gate6Validation\'+$case.name+'_'+$role+'.json'
  if(-not(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).LastWriteTime -lt $start){throw ('No fresh result '+$file)}
  $r=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json
  $failed=@($r.results|Where-Object {-not $_.pass})
  Write-Output ($case.name+' '+$role+' checks='+@($r.results).Count+' failures='+$failed.Count)
  if($failed.Count){$failed|ConvertTo-Json -Depth 8;throw ('Failed '+$case.name)}
  $r.PSObject.Properties.Remove('samples')
  $r|ConvertTo-Json -Depth 30|Set-Content -LiteralPath ($root+'\Docs\Gate6Results\'+$case.name+'_'+$role+'.json')
 }
 $errors=Select-String -LiteralPath ($root+'\Saved\Gate6Validation\'+$case.name+'.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
 if($errors){$errors|Select-Object -Last 10;throw 'Editor errors'}
 $compare=if($moving){'compare_moving.py'}else{'compare_resources.py'}
 & $python ($root+'\Tools\Validation\Gate6\'+$compare) $case.name
 if($LASTEXITCODE -ne 0){throw ('Paired comparison '+$case.name)}
 Write-Output ('COMPLETE '+$case.name)
}
