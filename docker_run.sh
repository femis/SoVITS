#!/bin/bash
echo "正在解压环境依赖..."

# 判断文件是否存在
if [ -f /opt/venv.tar.gz ]; then
    # 判断目标文件夹是否存在
    if [ ! -d /opt/venv ]; then
        tar -xzf /opt/venv.tar.gz -C /opt
        echo "venv解压完成"
    else
        echo "文件夹已存在"
    fi
else
    echo "压缩文件已被删除"
fi

sleep 2

# 判断文件是否存在
if [ -f /opt/venv.tar.gz ]; then
    rm -rf /opt/venv.tar.gz
fi

echo "正在下载预训练模型..."

# 判断文件是否存在
# 判断目标文件夹是否存在
if [ ! -d assets ]; then
    wget http://host.docker.internal:8080/sovits/assets.tar.gz
    echo "正在解压预训练模型..."
    tar -xzf assets.tar.gz
    echo "正在解压完成"
else
     echo "预训练模型文件夹已存在"
fi

echo "正在下载英文分词..."

# 判断文件是否存在
# 判断目标文件夹是否存在
if [ ! -d /root/nltk_data ]; then
    wget http://host.docker.internal:8080/sovits/nltk.tar.gz
    echo "正在解压预训练模型..."
    tar -xzf nltk.tar.gz
    echo "英文分词解压完成"
else
     echo "英文分词已存在"
fi

sleep 3

echo "正在删除预训练模型压缩包..."

# 判断文件是否存在
if [ -f assets.tar.gz ]; then
    rm -rf assets.tar.gz
fi

export PYTHONPATH=/opt/venv:$PYTHONPATH

echo "正在启动服务..."

python3 api_run.py