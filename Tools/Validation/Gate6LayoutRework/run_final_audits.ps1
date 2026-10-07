param([switch]$EditorOnly)
$ErrorActionPreference='Stop'
# Stage established audits, adjusting only intentional saved Gate6 fixture changes.
# Existing maps, collision bounds and camera acceptance checks are unchanged.
$root='D:\GitHub\RVSurvival\RVSurvival'
$source=Get-Content -LiteralPath ($root+'\Tools\Validation\Gate6Refinement\run_final_audits.ps1') -Raw
$hook=@'
  $taskText=$taskText.Replace("counts['actors']==65 and counts['pickups']==14 and counts['storage']==5","counts['actors']==70 and counts['pickups']==14 and counts['storage']==9")
  $taskText=$taskText.Replace("exec(open('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6Refinement/asset_checks.py').read())","exec(open('D:/GitHub/RVSurvival/RVSurvival/Tools/Validation/Gate6LayoutRework/asset_checks.py').read())")
'@
$source=$source.Replace(" Set-Content -LiteralPath (`$root+'\Saved\Gate6RefinementAssets\'+`$taskName)", $hook+"`n Set-Content -LiteralPath (`$root+'\Saved\Gate6RefinementAssets\'+`$taskName)")
# Execute in this script's scope so EditorOnly retains its ordinary meaning.
Invoke-Expression $source.Replace('param([switch]$EditorOnly)','')
