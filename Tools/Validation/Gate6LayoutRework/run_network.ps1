param([string]$Driver='host',[switch]$Emulated,[switch]$Auxiliary,[ValidateSet('','Bed','RearSeat','Ladder')][string]$Disconnect='')
$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
foreach($name in @('launch_process.py','process_startup.py','process_ready.py')){
 $text=(Get-Content -LiteralPath ($root+'\Tools\Validation\Gate6Refinement\'+$name) -Raw).Replace('Gate6Refinement','Gate6LayoutRework')
 Set-Content -LiteralPath ($root+'\Saved\Gate6LayoutRework\'+$name) -Value $text -Encoding utf8
}
Copy-Item -LiteralPath ($root+'\Tools\Validation\Gate6LayoutRework\'+$(if($Disconnect){'process_disconnect.py'}elseif($Auxiliary){'process_auxiliary.py'}else{'process_refinement.py'})) -Destination ($root+'\Saved\Gate6LayoutRework\process_refinement.py')
$name='native_'+$Driver+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})
if($Auxiliary){$name='aux_'+$Driver+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})}
if($Disconnect){$name='disconnect_'+$Disconnect+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})}
$history=$root+'\Saved\Gate6LayoutRework\History\'+$name+'_'+(Get-Date -Format 'yyyyMMdd-HHmmss')
foreach($suffix in @('.log','_child.log','_server.json','_client.json')){
 $previous=$root+'\Saved\Gate6LayoutRework\'+$name+$suffix
 if(Test-Path -LiteralPath $previous){New-Item -ItemType Directory -Force -Path $history|Out-Null;Copy-Item -LiteralPath $previous -Destination $history}
}
$case=@{name=$name;driver=$Driver;network=[bool]$Emulated;disconnect=$Disconnect}
$case|ConvertTo-Json|Set-Content -LiteralPath ($root+'\Saved\Gate6LayoutRework\case.json') -Encoding utf8
$start=Get-Date
$args='"'+$root+'\RVSurvival.uproject" -ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6LayoutRework/launch_process.py" -abslog="'+$root+'\Saved\Gate6LayoutRework\'+$name+'.log"'
$job=Start-Process -FilePath 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $args -WindowStyle Hidden -PassThru
if(-not $job.WaitForExit(360000)){throw 'Inspect editor timeout; do not force-kill'}
$pids=@();$failures=@()
foreach($role in @('server','client')){
 $file=$root+'\Saved\Gate6LayoutRework\'+$name+'_'+$role+'.json'
 if(-not(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).LastWriteTime -lt $start){throw ('Missing fresh '+$role+' receipt')}
 $result=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json;$pids+=$result.pid
 $failed=@($result.results|Where-Object {-not $_.pass});$failures+=$failed
 Write-Output ($role+' checks='+$result.results.Count+' failed='+$failed.Count)
 if($failed.Count){$failed|ConvertTo-Json -Depth 5}
 $result.PSObject.Properties.Remove('samples')
 $result|ConvertTo-Json -Depth 20|Set-Content -LiteralPath ($root+'\Docs\Gate6LayoutRework\'+$name+'_'+$role+'.json') -Encoding utf8
}
if($pids[0] -eq $pids[1]){throw 'Expected separate process PIDs'}
foreach($suffix in @('.log','_child.log')){
 $errors=Select-String -LiteralPath ($root+'\Saved\Gate6LayoutRework\'+$name+$suffix) -Pattern 'LogPython: Error:','Fatal error:','World Memory Leaks:'
 if($errors){$errors|Select-Object -Last 6;$failures+='Editor error'}
}
if($failures.Count){throw ('Validation failures='+$failures.Count)}
