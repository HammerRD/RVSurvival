$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
New-Item -ItemType Directory -Force -Path ($root+'\Saved\Gate6PhysicalRegressions'),($root+'\Docs\Gate6PhysicalRefinement\Regressions')|Out-Null
foreach($file in Get-ChildItem -LiteralPath ($root+'\Tools\Validation\Gate6\Regressions') -Filter '*.py'){
 $text=(Get-Content -LiteralPath $file.FullName -Raw).Replace('Saved/Gate6Regressions/','Saved/Gate6PhysicalRegressions/').Replace('Docs/Gate6Results/Regressions/','Docs/Gate6PhysicalRefinement/Regressions/')
 Set-Content -LiteralPath ($root+'\Saved\Gate6PhysicalRegressions\'+$file.Name) -Value $text -Encoding utf8
}
$text=(Get-Content -LiteralPath ($root+'\Tools\Validation\Gate6\run_regressions.ps1') -Raw).Replace('Saved\Gate6Regressions\','Saved\Gate6PhysicalRegressions\').Replace('Saved/Gate6Regressions/','Saved/Gate6PhysicalRegressions/').Replace('Docs\Gate6Results\Regressions\','Docs\Gate6PhysicalRefinement\Regressions\')
Set-Content -LiteralPath ($root+'\Saved\Gate6PhysicalRegressions\run.ps1') -Value $text -Encoding utf8
