param([ValidateSet('host','client')][string]$Driver='host',[switch]$Emulated,[ValidateSet('','Roof','Ladder')][string]$Disconnect='',[ValidateSet('physical','native','storage','stations','doors')][string]$Mode='physical')
$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$folder=$root+'\Saved\Gate7AcceptedInterior'
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
foreach($file in @('launch_process.py','process_startup.py','process_ready.py','process_refinement.py')){Copy-Item -LiteralPath ($root+'\Tools\Validation\Gate7\AcceptedInterior\'+$file) -Destination ($folder+'\'+$file)}
if($Mode -ne 'physical'){
 $sourcePath=if($Mode -eq 'storage'){$root+'\Tools\Validation\Gate7\AcceptedInterior\process_storage.py'}else{$root+'\Tools\Validation\Gate6LayoutRework\process_'+$(if($Mode -eq 'native'){'refinement'}else{$Mode})+'.py'}
 $source=(Get-Content -LiteralPath $sourcePath -Raw).Replace('Saved/Gate6LayoutRework','Saved/Gate7AcceptedInterior')
 if($Mode -in @('storage','stations','doors')){
  $prefix=(Get-Content -LiteralPath ($root+'\Tools\Validation\Gate6LayoutRework\process_auxiliary.py') -Raw).Replace('Saved/Gate6LayoutRework','Saved/Gate7AcceptedInterior')
  $prefix=$prefix -replace '(?m)^exitpoint=next\(.*$', 'exitpoint=None # physical doorway, no teleport endpoint'
  Set-Content -LiteralPath ($folder+'\auxiliary_prefix.py') -Value $prefix -Encoding utf8
  $source=$source.Replace('Tools/Validation/Gate6LayoutRework/process_auxiliary.py','Saved/Gate7AcceptedInterior/auxiliary_prefix.py')
 }
 $source+="`nif config.get('network'):`n for setting,value in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+setting+' '+str(value),pc)`n"
 Set-Content -LiteralPath ($folder+'\process_refinement.py') -Value $source -Encoding utf8
}
$name='physical_'+$Driver+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})
if($Mode -ne 'physical'){$name=$Mode+'_'+$Driver+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})}
if($Disconnect){$name='disconnect_'+$Disconnect+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})}
$history=$folder+'\History\'+$name+'_'+(Get-Date -Format yyyyMMdd-HHmmss)
foreach($suffix in @('.log','_child.log','_server.json','_client.json')){
 $previous=$folder+'\'+$name+$suffix
 if(Test-Path -LiteralPath $previous){New-Item -ItemType Directory -Force -Path $history|Out-Null;Copy-Item -LiteralPath $previous -Destination $history}
}
@{name=$name;driver=$Driver;network=[bool]$Emulated;disconnect=$Disconnect}|ConvertTo-Json|Set-Content -LiteralPath ($folder+'\case.json') -Encoding utf8
$start=Get-Date
$sourceCheckpoint=(git -c core.fsmonitor=false rev-parse --short HEAD)
$moduleHash=(Get-FileHash -LiteralPath ($root+'\Binaries\Win64\UnrealEditor-RVSurvival.dll') -Algorithm SHA256).Hash
$arguments='"'+$root+'\RVSurvival.uproject" -ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate7AcceptedInterior/launch_process.py" -abslog="'+$folder+'\'+$name+'.log"'
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
 $result|Add-Member -NotePropertyName source_checkpoint -NotePropertyValue $sourceCheckpoint -Force
 $result|Add-Member -NotePropertyName module_sha256 -NotePropertyValue $moduleHash -Force
 $result|Add-Member -NotePropertyName evidence_kind -NotePropertyValue 'Native input diagnostics; full sustained hardware/manual controls pending' -Force
 $result|ConvertTo-Json -Depth 20|Set-Content -LiteralPath ($root+'\Docs\Gate7AcceptedInterior\'+$name+'_'+$role+'.json') -Encoding utf8
}
if($pids[0] -eq $pids[1]){throw 'Expected separate process PIDs'}
foreach($suffix in @('.log','_child.log')){
 $errors=Select-String -LiteralPath ($folder+'\'+$name+$suffix) -Pattern 'LogPython: Error:','Fatal error:','World Memory Leaks:'
 if($errors){$errors|Select-Object -Last 6;$failures+='Editor error'}
}
if($failures.Count){throw ('Validation failures='+$failures.Count)}
