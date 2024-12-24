import subprocess

# 定义要运行的Python文件路径和端口参数
script = "api_v8.py"
ports = [5006, 5007, 5008]  # 你可以根据需要更改这些端口号
# 启动子进程来运行每个脚本
processes = []
for port in ports:
    process = subprocess.Popen(["python", script, f"--port={port}"])
    processes.append(process)

# 等待所有子进程完成
for process in processes:
    process.wait()

print("所有脚本已运行完毕")
