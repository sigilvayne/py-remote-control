# Показує невдалі входи по RDP за останні 7 днів
Get-WinEvent -FilterHashtable @{
    LogName='Security';
    ID=4625;
    StartTime=(Get-Date).AddDays(-7)
} | Where-Object {
    $_.Properties[18].Value -eq "10"  # Logon Type 10 = RDP
} | Select-Object TimeCreated, @{Name="Account";Expression={$_.Properties[5].Value}}, Message |
Format-Table -AutoSize
