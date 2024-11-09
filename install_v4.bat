@echo off
:: 安装服务
nssm install api4 "E:\www\SoVITS\runtime\python.exe" "E:\www\SoVITS\api_v4.py"
:: 设置工作目录
nssm set api4 AppDirectory E:\www\SoVITS
:: 设置标准输出日志文件（可选，路径可以根据需要更改）
nssm set api4 AppStdout E:\www\SoVITS\logs\api4_stdout.log
:: 设置标准错误日志文件（可选，路径可以根据需要更改）
nssm set api4 AppStderr E:\www\SoVITS\logs\api4_stderr.log
:: 提示用户服务已配置
echo Service api5 has been installed and configured with logging.