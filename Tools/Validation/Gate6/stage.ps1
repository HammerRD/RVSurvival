$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Stop the editor before staging test scripts'}
foreach($name in @('Gate6Validation','Gate6Regressions','Gate3Validation','Gate1Validation','Gate2Validation','Gate6FrontAudit','Gate6Camera')){
 New-Item -ItemType Directory -Path ($root+'\Saved\'+$name) -Force | Out-Null
}
Get-ChildItem -LiteralPath ($root+'\Tools\Validation\Gate6') -Filter '*.py' | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination ($root+'\Saved\Gate6Validation\'+$_.Name)}
Get-ChildItem -LiteralPath ($root+'\Tools\Validation\Gate6\Regressions') -Filter '*.py' | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination ($root+'\Saved\Gate6Regressions\'+$_.Name)}
foreach($pair in @(@('FrontAudit','Gate6FrontAudit'),@('Camera','Gate6Camera'))){
 Get-ChildItem -LiteralPath ($root+'\Tools\Validation\Gate6\'+$pair[0]) -Filter '*.py' | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination ($root+'\Saved\'+$pair[1]+'\'+$_.Name)}
}
# Recover missing accepted helpers without replacing a locally staged version.
$helpers=@(
 @('Tools\Validation\runner_runtime.py','Saved\Gate3Validation\runner_runtime.py'),
 @('Docs\Gate3Results\2026-10-05\Scripts\gate1_timeline.py','Saved\Gate3Validation\gate1_timeline.py'),
 @('Docs\Gate2Results\2026-10-05\gate1_scripts\single.py','Saved\Gate1Validation\single.py'),
 @('Docs\Gate2Results\2026-10-05\gate1_scripts\multi.py','Saved\Gate1Validation\multi.py'),
 @('Docs\Gate2Results\2026-10-05\multi.py','Saved\Gate2Validation\multi.py')
)
foreach($pair in $helpers){if(-not(Test-Path -LiteralPath ($root+'\'+$pair[1]))){Copy-Item -LiteralPath ($root+'\'+$pair[0]) -Destination ($root+'\'+$pair[1])}}
Write-Output 'Gate 6 scripts staged; saved maps, receipts and vendor assets were not altered.'
