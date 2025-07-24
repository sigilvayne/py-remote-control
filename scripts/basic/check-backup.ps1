# Перевірка вмісту папки C:\backup та підпапок з датами створення
$backupPath = "C:\backup"

if (-not (Test-Path $backupPath)) {
    Write-Output "Папка $backupPath не знайдена."
    exit 1
}

function List-FolderContents {
    param(
        [string]$Path,
        [string]$Indent = ""
    )
    $items = Get-ChildItem -Path $Path
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            Write-Output ("$Indent[Папка] " + $item.Name)
            List-FolderContents -Path $item.FullName -Indent ("  " + $Indent)
        } else {
            $date = $item.CreationTime.ToString("yyyy-MM-dd HH:mm:ss")
            Write-Output ("$Indent- $($item.Name) (створено: $date)")
        }
    }
}

Write-Output "Вміст ${backupPath}:"
List-FolderContents -Path $backupPath 