param([switch]$EditorOnly)
$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$engine='D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$python='D:\Epic Games\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
foreach($taskSet in @(@{source='FrontAudit';destination='Gate6RefinementFront';old='Gate6FrontAudit'},@{source='Camera';destination='Gate6RefinementCamera';old='Gate6Camera'})){
 New-Item -ItemType Directory -Force -Path ($root+'\Saved\'+$taskSet.destination)|Out-Null
 foreach($taskFile in Get-ChildItem -LiteralPath ($root+'\Tools\Validation\Gate6\'+$taskSet.source) -Filter '*.py'){
  $taskText=(Get-Content -LiteralPath $taskFile.FullName -Raw).Replace($taskSet.old,$taskSet.destination)
  Set-Content -LiteralPath ($root+'\Saved\'+$taskSet.destination+'\'+$taskFile.Name) -Value $taskText
 }
}
New-Item -ItemType Directory -Force -Path ($root+'\Saved\Gate6RefinementAssets')|Out-Null
foreach($taskName in @('editor_final.py','run_editor_final.py')){
 $taskText=(Get-Content -LiteralPath ($root+'\Tools\Validation\Gate6\'+$taskName) -Raw).Replace('Gate6Validation','Gate6RefinementAssets').Replace('Tools/Validation/Gate6/editor_final.py','Saved/Gate6RefinementAssets/editor_final.py')
 if($taskName -eq 'editor_final.py'){
  $taskText=$taskText.Replace('gate6=inspect_gate6()',"gate6=inspect_gate6()`nexec(open('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6Refinement/asset_checks.py').read())`ninspect_refined_assets(check)")
 }
 Set-Content -LiteralPath ($root+'\Saved\Gate6RefinementAssets\'+$taskName) -Value $taskText
}
$cases=@(
 @{name='refinement-exterior';runner='Saved/Gate6RefinementFront/run.py';receipt='Saved/Gate6RefinementFront/exterior.json'},
 @{name='refinement-camera';runner='Saved/Gate6RefinementCamera/launch_camera.py';receipt='Saved/Gate6RefinementCamera/camera.json'},
 @{name='refinement-editor';runner='Saved/Gate6RefinementAssets/run_editor_final.py';receipt='Saved/Gate6RefinementAssets/editor-final.json'}
)
if($EditorOnly){$cases=@($cases|Where-Object {$_.name -eq 'refinement-editor'})}
foreach($case in $cases){
 if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
 $started=Get-Date;$q=[char]34
 Write-Output ('START '+$case.name)
 $args=$q+$root+'\RVSurvival.uproject'+$q+' -ExecCmds='+$q+'py '+$root.Replace('\','/')+'/'+$case.runner+$q+' -abslog='+$q+$root+'\Saved\Gate6Refinement\'+$case.name+'.log'+$q
 $job=Start-Process -FilePath $engine -ArgumentList $args -WindowStyle Hidden -PassThru
 if(-not $job.WaitForExit(420000)){throw ('Editor timeout '+$case.name)}
 $file=$root+'/'+$case.receipt
 if(-not(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).LastWriteTime -lt $started){throw ('Fresh receipt missing '+$file)}
 & $python ($root+'\Tools\Validation\Gate6\Regressions\validate_receipt.py') $file
 if($LASTEXITCODE -ne 0){throw ('Failed '+$case.name)}
 $err=Select-String -LiteralPath ($root+'\Saved\Gate6Refinement\'+$case.name+'.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
 if($err){$err|Select-Object -Last 8;throw ('Editor error '+$case.name)}
 $r=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json
 $r.PSObject.Properties.Remove('samples')
 $r|ConvertTo-Json -Depth 30|Set-Content -LiteralPath ($root+'\Docs\Gate6Refinement\'+$case.name+'.json')
 Write-Output ('COMPLETE '+$case.name)
}
