$ErrorActionPreference='Stop'
$taskRoot='D:\GitHub\RVSurvival\RVSurvival'
New-Item -ItemType Directory -Force -Path ($taskRoot+'\Saved\Gate6RefinementRegressions'),($taskRoot+'\Saved\Gate6RefinementMoving'),($taskRoot+'\Docs\Gate6Refinement\Regressions')|Out-Null
foreach($taskFile in Get-ChildItem -LiteralPath ($taskRoot+'\Tools\Validation\Gate6\Regressions') -Filter '*.py'){
 $taskText=Get-Content -LiteralPath $taskFile.FullName -Raw
 $taskText=$taskText.Replace('Saved/Gate6Regressions/','Saved/Gate6RefinementRegressions/').Replace('Docs/Gate6Results/Regressions/','Docs/Gate6Refinement/Regressions/')
 Set-Content -LiteralPath ($taskRoot+'\Saved\Gate6RefinementRegressions\'+$taskFile.Name) -Value $taskText
}
$taskText=Get-Content -LiteralPath ($taskRoot+'\Tools\Validation\Gate6\run_regressions.ps1') -Raw
$taskText=$taskText.Replace('Saved\Gate6Regressions\','Saved\Gate6RefinementRegressions\').Replace('Saved/Gate6Regressions/','Saved/Gate6RefinementRegressions/').Replace('Docs\Gate6Results\Regressions\','Docs\Gate6Refinement\Regressions\')
Set-Content -LiteralPath ($taskRoot+'\Saved\Gate6RefinementRegressions\run.ps1') -Value $taskText
foreach($taskName in @('run_moving.py','launch_moving.py','moving_startup.py','moving_ready.py','process_moving.py','moving_resources.py')){
 $taskText=Get-Content -LiteralPath ($taskRoot+'\Tools\Validation\Gate6\'+$taskName) -Raw
 $taskText=$taskText.Replace('Saved/Gate6Validation/','Saved/Gate6RefinementMoving/')
 if($taskName -eq 'process_moving.py'){
  $taskText=$taskText.Replace('def setup():',"def setup():`n if isServer:`n  door=sv.get_editor_property('HouseDoor')`n  if door and not door.get_editor_property('bOpen'):door.complete_interaction(wp)")
  $taskText=$taskText.Replace("rest_test_point.get_editor_property('Occupant') is not None and frame_ok()","rest_test_point.get_editor_property('Occupant') is not None and wp.get_component_by_class(unreal.RVRestPoseComponent).get_editor_property('RestPoint')==rest_test_point")
 }
 if($taskName -eq 'launch_moving.py'){
  $taskText=$taskText.Replace("unreal.log('GATE4_NETWORK_CONFIG '+str(n))","s.set_editor_property('AdditionalLaunchParameters','-ExecCmds='+chr(34)+'py D:/GitHub/RVSurvival/RVSurvival/Saved/Gate6RefinementMoving/moving_startup.py'+chr(34)+' -abslog='+chr(34)+B+config['name']+'_child.log'+chr(34))`nunreal.log('GATE4_NETWORK_CONFIG '+str(n))")
 }
 Set-Content -LiteralPath ($taskRoot+'\Saved\Gate6RefinementMoving\'+$taskName) -Value $taskText
}
$taskText=Get-Content -LiteralPath ($taskRoot+'\Tools\Validation\Gate6\compare_moving.py') -Raw
$taskText=$taskText.Replace('Saved/Gate6Validation/','Saved/Gate6RefinementMoving/').Replace("'Saved/Gate6Validation'","'Saved/Gate6RefinementMoving'").Replace("'Docs/Gate6Results'","'Docs/Gate6Refinement'")
Set-Content -LiteralPath ($taskRoot+'\Saved\Gate6RefinementMoving\compare.py') -Value $taskText
