#!/bin/bash
# 定义要压缩的文件夹路径数组
folders=(
    "GPT_weights"
    "GPT_weights_v2"
    "SoVITS_weights"
    "SoVITS_weights_v2"
    "GPT_SoVITS"
    "tools"
)

# 切换到父目录并使用相对路径打包
cd /mnt/e/www/SoVITS || exit 1
tar -czf ./assets.tar.gz "${folders[@]}"