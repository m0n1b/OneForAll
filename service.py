import os
import subprocess
from pathlib import Path

# 获取脚本所在目录
script_dir = Path(__file__).parent

# 服务文件内容
service_content = f"""[Unit]
Description=Run telegram.py script every two hours
After=network.target

[Service]
ExecStart=/usr/bin/python3 {script_dir}/telegram.py
WorkingDirectory={script_dir}
Restart=always
User={os.getlogin()}
Group={os.getlogin()}
Environment=PATH={os.environ['PATH']}

[Install]
WantedBy=multi-user.target
"""

# 创建服务文件路径
service_file_path = "/etc/systemd/system/te_aw.service"

# 创建并写入服务文件
with open(service_file_path, 'w') as service_file:
    service_file.write(service_content)

# 刷新 systemd 服务
subprocess.run(['sudo', 'systemctl', 'daemon-reload'])

# 启动服务
subprocess.run(['sudo', 'systemctl', 'start', 'te_aw.service'])

# 设置服务开机启动
subprocess.run(['sudo', 'systemctl', 'enable', 'te_aw.service'])

# 创建cron定时任务（每两小时重启一次）
cron_job = "0 */2 * * * /usr/bin/systemctl restart te_aw.service"

# 获取当前用户的crontab文件
crontab_cmd = f"(crontab -l 2>/dev/null; echo \"{cron_job}\") | crontab -"

# 设置定时任务
subprocess.run(crontab_cmd, shell=True)

print("服务文件和定时任务已成功创建并启动！")
