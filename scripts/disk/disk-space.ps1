Get-PSDrive -PSProvider FileSystem | ForEach-Object {
    $total = $_.Used + $_.Free
    [PSCustomObject]@{
        'Диск'            = $_.Name
        'Загальний_обсяг_GB' = "{0:N2}" -f ($total / 1GB)
        'Використано_GB'     = "{0:N2}" -f ($_.Used / 1GB)
        'Вільно_GB'          = "{0:N2}" -f ($_.Free / 1GB)
        'Вільно_%'           = "{0:N1}" -f (($_.Free / $total) * 100)
    }
} | Format-Table -AutoSize
