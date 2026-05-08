# Get LAN IP, prioritize 192.168.x.x
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -match '^192\.168\.' } | Select-Object -First 1).IPAddress
if (-not $ip) {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
        $_.IPAddress -notmatch '^(127|169|172\.(1[6-9]|2[0-9]|3[01])\.)'
    } | Select-Object -First 1).IPAddress
}
if (-not $ip) { $ip = '127.0.0.1' }
Write-Output $ip
