$ErrorActionPreference='Stop'
$root='D:/GitHub/RVSurvival/RVSurvival';$base=$root+'/Saved/Gate8MechanicalRegression/'
if(Get-Process UnrealEditor -ErrorAction SilentlyContinue){throw 'Editor still running'}
# Reuse the already-staged safe Gate 8 lifecycle and child readiness scripts.
$source=(Get-Content ($root+'/Tools/Validation/Gate6PhysicalRefinement/process_refinement.py') -Raw).Replace('Saved/Gate6PhysicalRefinement','Saved/Gate8MechanicalRegression').Replace('Gate6FuelElectricalTest','Gate7MechanicalTest')
$source|Set-Content ($base+'process_refinement.py') -Encoding utf8
$name='final_physical_host_100ms_2loss'
@{name=$name;driver='host';network=$true}|ConvertTo-Json|Set-Content ($base+'case.json') -Encoding utf8
$began=Get-Date
$args='"'+$root+'/RVSurvival.uproject" -ExecCmds="py '+$base+'launch_process.py" -abslog="'+$base+$name+'.log"'
$job=Start-Process 'D:/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $args -WindowStyle Hidden -PassThru
while(!$job.HasExited){Start-Sleep -Seconds 2;if((Get-Date)-$began -gt [TimeSpan]::FromMinutes(5)){throw 'Inspect timeout; do not force kill'}}
$job.Dispose();$failed=0;$pids=@()
foreach($role in @('server','client')){
 $path=$base+$name+'_'+$role+'.json';if(!(Test-Path $path) -or (Get-Item $path).LastWriteTime -lt $began){throw 'Missing fresh receipt'}
 $r=Get-Content $path -Raw|ConvertFrom-Json;$bad=@($r.results|Where-Object{-not $_.pass});$failed+=$bad.Count;$pids+=$r.pid
 Write-Output "$role checks=$($r.results.Count) failed=$($bad.Count)";if($bad.Count){$bad|ConvertTo-Json -Depth 5}
 $r.PSObject.Properties.Remove('samples');$r|ConvertTo-Json -Depth 30|Set-Content ($root+'/Docs/Gate8Results/MechanicalRegression/'+$name+'_'+$role+'.json') -Encoding utf8
}
if($pids[0] -eq $pids[1]){throw 'Expected separate processes'}
foreach($suffix in @('.log','_child.log')){if(Select-String -Path ($base+$name+$suffix) -Pattern 'World Memory Leaks:','Fatal error:','LogPython: Error:'){throw 'Inspect preserved editor error'}}
if($failed){throw 'Inspect failed checks'}
