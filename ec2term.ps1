# ttermpro.exeのフルパス指定
Set-Variable -name TTERM -value ".\ttermpro.exe" -option constant
# SSH秘密鍵のフルパス指定
Set-Variable -name KEYFILE -value "hoge.pem" -option constant
# known_hostsのセキュリティ警告を表示するか
Set-Variable -name SECWAR -value $true -option constant

if ($TTERM -eq "") {
    Write-Host "ttermpro.exeのパスを指定してください"
    exit
}
if ($KEYFILE -eq "") {
    Write-Host "秘密鍵のパスを指定してください"
    exit
}

$target = Get-Clipboard
if ($target -eq $null) {
    # クリップボードが空
    $target = Read-Host "SSH Target"
} else {
    # クリップボード検証
    if ($target -notmatch "\S+\.\S+") {
        Write-Host "クリップボードの接続先が正しくありません"
        exit
    }
}
Write-Host "Connecting to $target"
if ($SECWAR) {
    & "$TTERM" ec2-user@$target`:22 /ssh2 /auth=publickey /keyfile="$KEYFILE"
} else {
    & "$TTERM" ec2-user@$target`:22 /ssh2 /auth=publickey /keyfile="$KEYFILE" /nosecuritywarning
}
