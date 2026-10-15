# Khoi dong RabbitMQ broker (ban zip, khong can quyen admin) tren may nay.
# RabbitMQ 4.3.6 + Erlang OTP 28 nam trong %USERPROFILE%\rabbitmq.
# Chay:  powershell -ExecutionPolicy Bypass -File .\start_rabbitmq.ps1
# Dung broker: Ctrl+C (hoac dong cua so).

$root = Join-Path $env:USERPROFILE "rabbitmq"
$env:ERLANG_HOME = Join-Path $root "otp28"
$env:RABBITMQ_BASE = Join-Path $root "data"
New-Item -ItemType Directory -Force $env:RABBITMQ_BASE | Out-Null

& (Join-Path $root "rabbitmq_server-4.3.6\sbin\rabbitmq-server.bat")
