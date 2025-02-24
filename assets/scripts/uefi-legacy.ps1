$BootMode = bcdedit | Select-String "path.*efi"
if ($null -eq $BootMode) {
    $BootMode = "Legacy"
}else {
    $BootMode = "UEFI"
}

Write-Output $BootMode