param([string]$Driver='host',[switch]$Emulated,[switch]$EntryProbe,[ValidateSet('mechanical','disconnect','native','stations','doors','auxiliary')][string]$Mode='mechanical')
$ErrorActionPreference='Stop'
$root='D:/GitHub/RVSurvival/RVSurvival';$base=$root+'/Saved/Gate7Validation/'
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Editor still running'}
& 'D:/Epic Games/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' ($root+'/Tools/Validation/Gate7/set_listen_preferences.py')
if($LASTEXITCODE -ne 0){throw 'Cannot configure listen-server mode'}
foreach($name in @('launch_process.py','process_startup.py','process_ready.py')){
 $source=Get-Content ($root+'/Tools/Validation/Gate6Refinement/'+$name) -Raw
 $source=$source.Replace('Gate6Refinement','Gate7Validation').Replace('Gate6FuelElectricalTest','Gate7MechanicalTest')
 if($name -eq 'process_ready.py'){
  $source=$source.Replace("house=vehicles[0].get_editor_property('HouseDoor')","service=vehicles[0].get_editor_property('EngineService')`n  hood=vehicles[0].get_editor_property('EngineHood')`n  if hood is None or hood.get_editor_property('DoorMesh') is None:return`n  if service is None or service.get_editor_property('Vehicle')!=vehicles[0] or service.get_attach_parent_actor()!=vehicles[0]:return`n  local=vehicles[0].get_actor_transform().inverse_transform_location(service.get_actor_location())`n  if abs(local.x-416)>1:return`n  house=vehicles[0].get_editor_property('HouseDoor')")
 }
 if($name -eq 'launch_process.py'){
  $source=$source.Replace("if t>240 and not ending:unreal.log_error('REFINE_TIMEOUT');", "if t>240 and not ending:`n  unreal.log_error('REFINE_TIMEOUT');")
  $source=$source.Replace('unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4',"from runner_runtime import release_runners`n  release_runners();unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4")
 }
 $source|Set-Content ($base+$name) -Encoding utf8
}
$runner=if($Mode -in @('mechanical','disconnect')){$root+'/Tools/Validation/Gate7/process_'+$Mode+'.py'}else{$root+'/Tools/Validation/Gate6LayoutRework/process_'+$(if($Mode -eq 'native'){'refinement'}else{$Mode})+'.py'}
$source=(Get-Content $runner -Raw).Replace('Saved/Gate6LayoutRework','Saved/Gate7Validation').Replace('Gate6FuelElectricalTest','Gate7MechanicalTest')
if($Mode -in @('stations','doors')){
 $prefix=(Get-Content ($root+'/Tools/Validation/Gate6LayoutRework/process_auxiliary.py') -Raw).Replace('Saved/Gate6LayoutRework','Saved/Gate7Validation').Replace('Gate6FuelElectricalTest','Gate7MechanicalTest')
 $prefix|Set-Content ($base+'auxiliary_prefix.py') -Encoding utf8
 $source=$source.Replace('Tools/Validation/Gate6LayoutRework/process_auxiliary.py','Saved/Gate7Validation/auxiliary_prefix.py')
}
$source+="`nif config.get('network'):`n for setting,value in [('PktLagMin',100),('PktLagMax',100),('PktLoss',2)]:unreal.SystemLibrary.execute_console_command(pc,'NetEmulation.'+setting+' '+str(value),pc)`n"
$source|Set-Content ($base+'process_refinement.py') -Encoding utf8
$name=$Mode+'_'+$Driver+$(if($Emulated){'_100ms_2loss'}else{'_baseline'})
if($EntryProbe){$name+='_entry_probe'}
@{name=$name;driver=$Driver;network=[bool]$Emulated;emulation_target='Everyone';entry_probe=[bool]$EntryProbe}|ConvertTo-Json|Set-Content ($base+'case.json') -Encoding utf8
$began=Get-Date
foreach($suffix in @('.log','_child.log','_server.json','_client.json')){if(Test-Path ($base+$name+$suffix)){New-Item -ItemType Directory -Force ($base+'History/'+$name+'-'+(Get-Date -Format yyyyMMddHHmmss))|Out-Null;Copy-Item ($base+$name+$suffix) ($base+'History/'+$name+'-'+(Get-Date -Format yyyyMMddHHmmss)+'/')}}
$args='"'+$root+'/RVSurvival.uproject" -ExecCmds="py '+$base+'launch_process.py" -abslog="'+$base+$name+'.log"'
$job=Start-Process 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $args -WindowStyle Hidden -PassThru
while(!$job.HasExited){Start-Sleep -Seconds 2;if((Get-Date)-$began -gt [TimeSpan]::FromMinutes(5)){throw 'Inspect timeout; do not force kill'}}
$job.Dispose();Start-Sleep -Seconds 1
$failures=0;$pids=@()
foreach($role in @('server','client')){
 $path=$base+$name+'_'+$role+'.json';if(!(Test-Path $path) -or (Get-Item $path).LastWriteTime -lt $began){throw "Missing fresh $role receipt"}
 $r=Get-Content $path -Raw|ConvertFrom-Json;$bad=@($r.results|Where-Object{-not $_.pass});Write-Output "$role checks=$($r.results.Count) failed=$($bad.Count)";if($bad.Count){$bad|ConvertTo-Json -Depth 5}
 $pids+=$r.pid
 $failures+=$bad.Count
 if($r.samples){$r|Add-Member -NotePropertyName sample_summary -NotePropertyValue @{count=$r.samples.Count;max_correction_cm=($r.samples.max_correction|Measure-Object -Maximum).Maximum;max_speed_cm_s=($r.samples.speed|Measure-Object -Maximum).Maximum} -Force;$r.PSObject.Properties.Remove('samples')}
 $r|ConvertTo-Json -Depth 30|Set-Content ($root+'/Docs/Gate7Results/'+$name+'_'+$role+'.json') -Encoding utf8
}
if($pids[0] -eq $pids[1]){throw 'Expected separate process PIDs'}
foreach($suffix in @('.log','_child.log')){if(Select-String -Path ($base+$name+$suffix) -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'){throw 'Editor or child error; inspect preserved log'}}
if($failures){throw "Failed checks=$failures; inspect preserved receipts"}
