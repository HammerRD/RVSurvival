$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$base=$root+'\Saved\Gate6PhysicalResources'
New-Item -ItemType Directory -Force -Path $base | Out-Null
foreach($name in @('launch_process.py','process_startup.py','process_ready.py','process.py')){
 $text=(Get-Content -LiteralPath ($root+'\Tools\Validation\Gate6\'+$name) -Raw).Replace('Saved/Gate6Validation/','Saved/Gate6PhysicalResources/')
 if($name -eq 'process.py'){
  # Use the actual surface-aligned power interaction, which opens the same panel.
  $text=$text.Replace('def focus(a):',"power_station=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RVInteriorStation) if str(a.get_editor_property('StationName'))=='Power')`ndef focus(a):")
  $text=$text.Replace('focus(panel)','focus(power_station)')
 }
 if($name -eq 'launch_process.py'){
  $text=$text.Replace("unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()","s.set_editor_property('AdditionalLaunchParameters','-ExecCmds='+chr(34)+'py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalResources/process_startup.py'+chr(34)+' -abslog='+chr(34)+B+'resources_child.log'+chr(34))`nunreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()")
  $text=$text.Replace("  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4","  from runner_runtime import release_runners`n  release_runners();unreal.log('LAYOUT_RESOURCE_RUNNERS_RELEASED_BEFORE_STOP')`n  unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4")
 }
 Set-Content -LiteralPath ($base+'\'+$name) -Value $text -Encoding utf8
}
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
@{name='resources';network=$true}|ConvertTo-Json|Set-Content ($base+'\case.json')
$start=Get-Date
$args='"'+$root+'\RVSurvival.uproject" -ExecCmds="py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6PhysicalResources/launch_process.py" -abslog="'+$base+'\resources.log"'
$job=Start-Process 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $args -WindowStyle Hidden -PassThru
if(-not $job.WaitForExit(300000)){throw 'Inspect timeout'}
foreach($role in @('server','client')){
 $file=$base+'\resources_'+$role+'.json'
 if((Get-Item $file).LastWriteTime -lt $start){throw 'Stale receipt'}
 $r=Get-Content $file -Raw|ConvertFrom-Json;$fails=@($r.results|Where-Object {-not $_.pass})
 Write-Output ($role+' resource checks='+$r.results.Count+' failures='+$fails.Count)
 $r.PSObject.Properties.Remove('samples');$r|ConvertTo-Json -Depth 30|Set-Content ($root+'\Docs\Gate6PhysicalRefinement\resources_'+$role+'.json')
 if($fails.Count){$fails|ConvertTo-Json -Depth 8;throw 'Resource regression failed'}
}
foreach($log in @('resources.log','resources_child.log')){
 if(Select-String -LiteralPath ($base+'\'+$log) -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'){throw 'Editor error'}
}

