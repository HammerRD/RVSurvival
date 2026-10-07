param([ValidateSet('host','client')][string]$Driver='host',[switch]$Emulated)
$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$folder=$root+'\Saved\Gate6PhysicalRefinement'
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
foreach($file in @('launch_process.py','process_startup.py','process_ready.py','process_refinement.py')){Copy-Item -LiteralPath ($root+'\Tools\Validation\Gate6PhysicalRefinement\'+$file) -Destination ($folder+'\'+$file)}
$name='physical_'+$Driver+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})
$history=$folder+'\History\'+$name+'_'+(Get-Date -Format yyyyMMdd-HHmmss)
foreach($suffix in @('.log','_child.log','_server.json','_client.json')){
 $previous=$folder+'\'+$name+$suffix
 if(Test-Path -LiteralPath $previous){New-Item -ItemType Directory -Force -Path $history|Out-Null;Copy-Item -LiteralPath $previous -Destination $history}
}
@{name=$name;driver=$Driver;network=[bool]$Emulated}|ConvertTo-Json|Set-Content -LiteralPath ($folder+'\case.json') -Encoding utf8
$start=Get-Date
$arguments='"'+$root+'\RVSurvival.uproject" -ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalRefinement/launch_process.py" -abslog="'+$folder+'\'+$name+'.log"'
$job=Start-Process -FilePath 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru
if(-not $job.WaitForExit(330000)){throw 'Inspect editor timeout; do not force-kill'}
$pids=@();$failures=@()
foreach($role in @('server','client')){
 $file=$folder+'\'+$name+'_'+$role+'.json'
 if(-not(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).LastWriteTime -lt $start){throw ('Missing fresh '+$role+' receipt')}
 $result=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json;$pids+=$result.pid
 $failed=@($result.results|Where-Object {-not $_.pass});$failures+=$failed
 Write-Output ($role+' checks='+$result.results.Count+' failed='+$failed.Count)
 if($failed.Count){$failed|ConvertTo-Json -Depth 5}
 $result.PSObject.Properties.Remove('samples')
 $result|ConvertTo-Json -Depth 20|Set-Content -LiteralPath ($root+'\Docs\Gate6PhysicalRefinement\'+$name+'_'+$role+'.json') -Encoding utf8
}
if($pids[0] -eq $pids[1]){throw 'Expected separate process PIDs'}
foreach($suffix in @('.log','_child.log')){
 $errors=Select-String -LiteralPath ($folder+'\'+$name+$suffix) -Pattern 'LogPython: Error:','Fatal error:','World Memory Leaks:'
 if($errors){$errors|Select-Object -Last 6;$failures+='Editor error'}
}
if($failures.Count){throw ('Validation failures='+$failures.Count)}
