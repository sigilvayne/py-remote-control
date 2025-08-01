
$rdpRules = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "RDPGuard*" }


$blockedIPs = @()
foreach ($rule in $rdpRules) {
    if ($rule.DisplayName -match '\b(\d{1,3}(\.\d{1,3}){3})\b') {
        $blockedIPs += $Matches[1]
    } else {
        $blockedIPs += "(unknown IP in rule: $($rule.DisplayName))"
    }
}

$count = $rdpRules.Count
$rdpRules | Remove-NetFirewallRule -Confirm:$false

$finalReport = @"
RDP GUARD UNBLOCK REPORT:
Firewall Rules Removed: $count

Unblocked IPs:
$($blockedIPs -join "`n")

✅ All RDPGuard-related blocks were removed from Windows Firewall.
"@

Write-Output $finalReport
