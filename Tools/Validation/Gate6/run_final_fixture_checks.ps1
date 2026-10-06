$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$engine='D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$python='D:\Epic Games\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'
$cases=@(
 @{name='final-single-fixture';runner='Tools/Validation/Gate6/launch_single.py';receipt='Saved/Gate6Validation/single.json'},
 @{name='editor-final-fixture';runner='Tools/Validation/Gate6/run_editor_final.py';receipt='Saved/Gate6Validation/editor-final.json'}
)
foreach($case in $cases){
 if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Refuse concurrent editor'}
 $started=Get-Date;$q=[char]34
 Write-Output ('START '+$case.name)
 $args=$q+$root+'\RVSurvival.uproject'+$q+' -ExecCmds='+$q+'py '+$root.Replace('\','/')+'/'+$case.runner+$q+' -abslog='+$q+$root+'\Saved\Gate6Validation\'+$case.name+'.log'+$q
 $job=Start-Process -FilePath $engine -ArgumentList $args -WindowStyle Hidden -PassThru
 if(-not $job.WaitForExit(240000)){throw ('Editor timeout '+$case.name)}
 $file=$root+'/'+$case.receipt
 if(-not(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).LastWriteTime -lt $started){throw ('Fresh receipt missing '+$file)}
 & $python ($root+'\Tools\Validation\Gate6\Regressions\validate_receipt.py') $file
 if($LASTEXITCODE -ne 0){throw ('Failed '+$case.name)}
 $err=Select-String -LiteralPath ($root+'\Saved\Gate6Validation\'+$case.name+'.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
 if($err){$err|Select-Object -Last 8;throw ('Editor error '+$case.name)}
 $r=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json
 $r.PSObject.Properties.Remove('samples')
 $r|ConvertTo-Json -Depth 30|Set-Content -LiteralPath ($root+'\Docs\Gate6Results\'+$case.name+'.json')
 Write-Output ('COMPLETE '+$case.name)
}
