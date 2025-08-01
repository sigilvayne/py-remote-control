$rdpRules = Get-NetFirewallRule | Where-Object {
    $_.DisplayName -match 'RDPGuard' -or $_.Description -match 'RDPGuard'
}

$rdpDetailed = @()
foreach ($rule in $rdpRules) {
    $filters = Get-NetFirewallAddressFilter -AssociatedNetFirewallRule $rule
    foreach ($filter in $filters) {
        $rdpDetailed += [PSCustomObject]@{
            RuleName   = $rule.DisplayName
            Direction  = $rule.Direction
            RemoteIP   = $filter.RemoteAddress
        }
    }
}

$finalReport = @"
RDP GUARD BLOCKED IP PREVIEW:
Total RDPGuard-related Rules Found: $($rdpRules.Count)
Blocked IP Entries Found: $($rdpDetailed.Count)

Details:
$($rdpDetailed | Format-Table -AutoSize | Out-String)

ℹ️ No changes were made. This is only a preview.
"@

Write-Output $finalReport
