# 第一阶段：安装依赖和预处理
FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04 AS builder

RUN sed -i 's@http://archive.ubuntu.com/ubuntu/@http://mirrors.tuna.tsinghua.edu.cn/ubuntu/@g' /etc/apt/sources.list && \
    sed -i 's@http://security.ubuntu.com/ubuntu/@http://mirrors.tuna.tsinghua.edu.cn/ubuntu/@g' /etc/apt/sources.list

# Install 3rd party apps
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ffmpeg libsox-dev libjpeg-dev libpng-dev parallel aria2 git git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /workspace

COPY requirements.txt /workspace/

# 安装依赖到集中目录并压缩
RUN mkdir -p /opt/venv && \
    pip install --target /opt/venv -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host=pypi.tuna.tsinghua.edu.cn && \
    cd /opt && \
    tar -czf venv.tar.gz venv && \
    rm -rf venv

COPY . .


# 第二阶段：最终应用构建
FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04

# 安装ffmpeg和其他必要的依赖
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ffmpeg libsox-dev libjpeg-dev libpng-dev parallel aria2 git git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# 复制第一阶段构建的结果
COPY --from=builder /opt/venv.tar.gz /opt/
COPY --from=builder /workspace /workspace

EXPOSE 5006 5007

# 修改 CMD 指令以运行 docker_run.sh 脚本
CMD ["/workspace/docker_run.sh"]