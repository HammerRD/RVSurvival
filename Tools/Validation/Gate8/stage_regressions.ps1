param([switch]$SkipCompleted)
$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
New-Item -ItemType Directory -Force -Path ($root+'\Saved\Gate8Regressions'),($root+'\Docs\Gate8Results\Regressions')|Out-Null
foreach($file in Get-ChildItem -LiteralPath ($root+'\Tools\Validation\Gate6\Regressions') -Filter '*.py'){
 $text=(Get-Content -LiteralPath $file.FullName -Raw).Replace('Saved/Gate6Regressions/','Saved/Gate8Regressions/').Replace('Docs/Gate6Results/Regressions/','Docs/Gate8Results/Regressions/')
 $text=$text.Replace("if t>90 and not ending:unreal.log_error('REFINE_TIMEOUT');", "if t>90 and not ending:`n  unreal.log_error('REFINE_TIMEOUT');")
 $text=$text.Replace('unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play();ending=time.time()+4',"from recovery_lifecycle import end_play_then_quit`n  end_play_then_quit(h);return")
 if($file.Name -eq 'gate2_final.py'){$text=$text.Replace('Saved/Gate2Validation/multi.py','Tools/Validation/Gate7/accepted_gate2_fixture.py')}
 $text="import sys`nsys.path.insert(0,'D:/GitHub/RVSurvival/RVSurvival/Saved/Gate8Regressions')`n"+$text
 Set-Content -LiteralPath ($root+'\Saved\Gate8Regressions\'+$file.Name) -Value $text -Encoding utf8
}
Copy-Item -LiteralPath ($root+'\Tools\Validation\Gate6PhysicalRefinement\recovery_lifecycle.py') -Destination ($root+'\Saved\Gate8Regressions\recovery_lifecycle.py')
$text=(Get-Content -LiteralPath ($root+'\Tools\Validation\Gate6\run_regressions.ps1') -Raw).Replace('Saved\Gate6Regressions\','Saved\Gate8Regressions\').Replace('Saved/Gate6Regressions/','Saved/Gate8Regressions/').Replace('Docs\Gate6Results\Regressions\','Docs\Gate8Results\Regressions\')
Set-Content -LiteralPath ($root+'\Saved\Gate8Regressions\run.ps1') -Value $text -Encoding utf8
if($SkipCompleted){
 $text=$text.Replace('foreach($case in $cases){', '$cases=@($cases|Where-Object {$_.name -notin @(''refined-entry'',''gate1'')})'+"`n"+'foreach($case in $cases){')
 Set-Content -LiteralPath ($root+'\Saved\Gate8Regressions\run.ps1') -Value $text -Encoding utf8
}
