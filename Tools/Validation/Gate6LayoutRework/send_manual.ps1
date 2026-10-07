param([Parameter(Mandatory)][string]$Json)
$ErrorActionPreference='Stop'
$base='D:\GitHub\RVSurvival\RVSurvival\Saved\Gate6LayoutRework'
$command=ConvertFrom-Json $Json -AsHashtable
$previous=Get-Content ($base+'\manual-command.json') -Raw|ConvertFrom-Json
$command.id=[int]$previous.id+1
for($attempt=0;$attempt -lt 20;$attempt++){
 try {$command|ConvertTo-Json|Set-Content ($base+'\manual-command.json') -Encoding utf8;break}
 catch {if($attempt -eq 19){throw};Start-Sleep -Milliseconds 50}
}
$deadline=(Get-Date).AddSeconds(10)
do {
 Start-Sleep -Milliseconds 100
 try {$state=Get-Content ($base+'\manual-current.json') -Raw|ConvertFrom-Json} catch {$state=$null}
} until(($state -and $state.command_id -eq $command.id) -or (Get-Date) -ge $deadline)
if(-not $state -or $state.command_id -ne $command.id){throw 'No current command acknowledgement'}
$pause=if($command.op -eq 'hold'){[int](1000*$command.seconds)+350}elseif($command.op -eq 'photo'){1600}else{650}
Start-Sleep -Milliseconds $pause
for($attempt=0;$attempt -lt 20;$attempt++){
 try {$state=Get-Content ($base+'\manual-current.json') -Raw|ConvertFrom-Json;if($state){break}}
 catch {if($attempt -eq 19){throw}}
 Start-Sleep -Milliseconds 50
}
if(-not $state){throw 'No complete current snapshot'}
@{command=$command;observed=$state}|ConvertTo-Json -Depth 7 -Compress|Add-Content ($base+'\manual-final-actions.jsonl') -Encoding utf8
$state|ConvertTo-Json -Depth 5
