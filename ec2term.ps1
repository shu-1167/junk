# ttermpro.exe�̃t���p�X�w��
Set-Variable -name TTERM -value ".\ttermpro.exe" -option constant
# SSH�閧���̃t���p�X�w��
Set-Variable -name KEYFILE -value "hoge.pem" -option constant
# known_hosts�̃Z�L�����e�B�x����\�����邩
Set-Variable -name SECWAR -value $true -option constant

if ($TTERM -eq "") {
    Write-Host "ttermpro.exe�̃p�X���w�肵�Ă�������"
    exit
}
if ($KEYFILE -eq "") {
    Write-Host "�閧���̃p�X���w�肵�Ă�������"
    exit
}

$target = Get-Clipboard
if ($target -eq $null) {
    # �N���b�v�{�[�h����
    $target = Read-Host "SSH Target"
} else {
    # �N���b�v�{�[�h����
    if ($target -notmatch "\S+\.\S+") {
        Write-Host "�N���b�v�{�[�h�̐ڑ��悪����������܂���"
        exit
    }
}
Write-Host "Connecting to $target"
if ($SECWAR) {
    & "$TTERM" ec2-user@$target`:22 /ssh2 /auth=publickey /keyfile="$KEYFILE"
} else {
    & "$TTERM" ec2-user@$target`:22 /ssh2 /auth=publickey /keyfile="$KEYFILE" /nosecuritywarning
}
