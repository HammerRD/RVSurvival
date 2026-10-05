$taskEvidence = Join-Path $PSScriptRoot '../../Docs/Gate3Results/2026-10-05/Gate2Regression'
$taskEvidence = [IO.Path]::GetFullPath($taskEvidence)
$taskRows = @()
foreach ($taskMode in @('separate_process','network')) {
    $taskHost = Get-Content -LiteralPath (Join-Path $taskEvidence ($taskMode + '_host.json')) -Raw | ConvertFrom-Json
    $taskClient = Get-Content -LiteralPath (Join-Path $taskEvidence ($taskMode + '_client.json')) -Raw | ConvertFrom-Json
    foreach ($taskName in @('fresh','host_driver','both_host_driving','host_drive','host_stopped','both_exited','client_driver','both_client_driving','client_drive','client_stopped')) {
        $taskA = $taskHost.samples.$taskName; $taskB = $taskClient.samples.$taskName
        $taskDelta = 0.0
        for ($taskAxis = 0; $taskAxis -lt 3; $taskAxis++) { $taskDelta += [Math]::Pow($taskA.position[$taskAxis] - $taskB.position[$taskAxis], 2) }
        $taskDelta = [Math]::Sqrt($taskDelta)
        $taskLimit = if ($taskMode -eq 'network' -and $taskName -in @('host_drive','client_drive')) { 250 } else { 100 }
        $taskAgree = ($taskA.seats.DriverSeat -eq $taskB.seats.DriverSeat) -and ($taskA.seats.PassengerSeat -eq $taskB.seats.PassengerSeat)
        $taskRows += [ordered]@{case=($taskMode + '_' + $taskName + '_replication');pass=($taskAgree -and $taskDelta -lt $taskLimit);distance_cm=$taskDelta;limit_cm=$taskLimit;seat_occupancy_agrees=$taskAgree;server_gravity=$taskA.proxy_gravity_enabled;client_gravity=$taskB.proxy_gravity_enabled}
    }
}
$taskRows | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskEvidence 'replication_comparison.json') -Encoding utf8
$taskCounts = @()
foreach ($taskFile in @('shared_multi.json','concurrent_seat_claim.json','separate_process_host.json','separate_process_client.json','network_host.json','network_client.json','passenger_disconnect_host.json','passenger_disconnect_client.json','replication_comparison.json')) {
    $taskData = Get-Content -LiteralPath (Join-Path $taskEvidence $taskFile) -Raw | ConvertFrom-Json
    $taskCases = if ($taskData.PSObject.Properties.Name -contains 'results') { @($taskData.results) } else { @($taskData) }
    $taskCounts += [ordered]@{file=$taskFile;passed=@($taskCases | Where-Object pass -eq $true).Count;failed=@($taskCases | Where-Object pass -ne $true).Count;total=$taskCases.Count}
}
$taskCounts | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskEvidence 'assertion_summary.json') -Encoding utf8
$taskCounts | ForEach-Object { [pscustomobject]$_ } | Format-Table -AutoSize
$taskRows | ForEach-Object { [pscustomobject]$_ } | Select-Object case,distance_cm,pass | Format-Table -AutoSize


