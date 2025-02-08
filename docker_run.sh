#!/bin/bash
echo "正在解压环境依赖..."

tar -xzf /opt/venv.tar.gz -C /opt

sleep 3

rm -rf /opt/venv.tar.gz

echo "正在解压完成"

wget http://host.docker.internal:8080/sovits/assets.tar.gz

echo "正在解压预训练模型..."

tar -xzf assets.tar.gz

echo "正在解压完成"

sleep 3

echo "正在删除预训练模型压缩包..."

rm -rf assets.tar.gz

echo

export PYTHONPATH=/opt/venv:$PYTHONPATH

echo "正在启动服务..."

python3 api_run.py