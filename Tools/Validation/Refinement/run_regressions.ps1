$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$engine='D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$cases=@(
 @{name='refined-entry';runner='run_single_final.py';file='Saved\Gate5Refinement\single-final.json'},
 @{name='gate1';runner='run_gate1_final.py';file='Docs\Gate5Refinement\Gate1Regression\summary.json'},
 @{name='gate2';runner='run_gate2_final.py';file='Docs\Gate5Refinement\Gate2Regression\shared.json'},
 @{name='inventory';runner='run_inventory_regression.py';file='Saved\Gate5Refinement\full.json'},
 @{name='needs';runner='run_needs.py';file='Saved\Gate5Refinement\needs-single.json'}
)
foreach($case in $cases){
 $started=Get-Date;$q=[char]34
 Write-Output ('START regression '+$case.name)
 $args=$q+$root+'\RVSurvival.uproject'+$q+' -ExecCmds='+$q+'py '+$root.Replace('\','/')+'/Saved/Gate5Refinement/'+$case.runner+$q+' -abslog='+$q+$root+'\Saved\Gate5Refinement\regression-'+$case.name+'.log'+$q
 $job=Start-Process -FilePath $engine -ArgumentList $args -WindowStyle Hidden -PassThru
 if(-not $job.WaitForExit(240000)){throw ('Editor timeout '+$case.name)}
 $receipt=$root+'\'+$case.file
 if(-not(Test-Path -LiteralPath $receipt) -or (Get-Item -LiteralPath $receipt).LastWriteTime -lt $started){throw ('Fresh receipt missing '+$receipt)}
 & 'D:\Epic Games\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' ($root+'\Saved\Gate5Refinement\validate_receipt.py') $receipt
 if($LASTEXITCODE -ne 0){throw ('Regression failed '+$case.name)}
 $err=Select-String -LiteralPath ($root+'\Saved\Gate5Refinement\regression-'+$case.name+'.log') -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'
 if($err){$err|Select-Object -Last 8;throw ('Editor error '+$case.name)}
 if($case.name -in @('inventory','needs','refined-entry')){
  Copy-Item -LiteralPath $receipt -Destination ($root+'\Docs\Gate5Refinement\regression-'+$case.name+'.json')
 }
}
