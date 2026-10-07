$ErrorActionPreference='Stop'
$root='D:\GitHub\RVSurvival\RVSurvival'
$original=Get-Content -LiteralPath ($root+'\Docs\Gate3Results\2026-10-05\vendor_source_hashes.json') -Raw|ConvertFrom-Json
$changed=@($original|Where-Object {(Get-FileHash -LiteralPath $_.Path -Algorithm SHA256).Hash -ne $_.Hash})
$content=@(git -c core.fsmonitor=false diff --name-only fce8422 -- Content)
$allowed=@('Content/Maps/Gate6FuelElectricalTest.umap','Content/Vehicles/Gate6/BP_ClassCSystemsMotorhome.uasset')
if(@($content|Where-Object {$_ -notin $allowed}).Count){throw 'Unexpected saved content change'}
if($changed.Count -or $original.Count -ne 108){throw 'Vendor integrity failed'}
$map=Get-Item -LiteralPath ($root+'\'+$allowed[0]);$blueprint=Get-Item -LiteralPath ($root+'\'+$allowed[1])
@{checked=$original.Count;changed=0;changed_paths=@();checked_at=(Get-Date -Format o)}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath ($root+'\Docs\Gate6PhysicalRefinement\vendor-integrity.json')
$assets=@($map,$blueprint)|ForEach-Object {@{path=$_.FullName;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash;modified=$_.LastWriteTime.ToString('o')}}
@{engine_association=(Get-Content -LiteralPath ($root+'\RVSurvival.uproject') -Raw|ConvertFrom-Json).EngineAssociation;assets=$assets;vendor_files=108;unexpected_content_changes=0;compared_to='fce8422';checked_at=(Get-Date -Format o)}|ConvertTo-Json -Depth 6|Set-Content -LiteralPath ($root+'\Docs\Gate6PhysicalRefinement\saved-state-verification.json')
git -c core.fsmonitor=false diff --name-only fce8422 -- Source Content Config/DefaultInput.ini |Set-Content -LiteralPath ($root+'\Docs\Gate6PhysicalRefinement\source-content-manifest.txt')
Write-Output 'Verified 108 vendor hashes, saved Gate6 map/Blueprint, canonical engine association and unchanged other content.'
