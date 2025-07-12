param (
    [string]$url
)

if (-not $url) {
    Write-Error "URL не передано"
    exit 1
}

$tempPath = "C:\Script\agent\tmp"
New-Item -ItemType Directory -Force -Path $tempPath | Out-Null

$fileName = Split-Path -Leaf $url
$destination = Join-Path $tempPath $fileName

Invoke-WebRequest -Uri $url -OutFile $destination
Write-Output "Завантажено: $destination"
