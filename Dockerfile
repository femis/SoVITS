# 第一阶段：安装依赖和预处理
FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04 AS builder

LABEL maintainer="breakstring@hotmail.com"
LABEL version="dev-20240209"
LABEL description="Docker image for GPT-SoVITS"

RUN sed -i 's@http://archive.ubuntu.com/ubuntu/@http://mirrors.aliyun.com/ubuntu/@g' /etc/apt/sources.list && \
    sed -i 's@http://security.ubuntu.com/ubuntu/@http://mirrors.aliyun.com/ubuntu/@g' /etc/apt/sources.list

# Install 3rd party apps
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ffmpeg libsox-dev libjpeg-dev libpng-dev parallel aria2 git git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt initially to leverage Docker cache
WORKDIR /workspace
COPY requirements.txt /workspace/
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Define a build-time argument for image type
ARG IMAGE_TYPE=elite

# Conditional logic based on the IMAGE_TYPE argument
# Always copy the Docker directory, but only use it if IMAGE_TYPE is not "elite"
COPY ./Docker /workspace/Docker 
# elite 类型的镜像里面不包含额外的模型
RUN if [ "$IMAGE_TYPE" != "elite" ]; then \
		chmod +x /workspace/Docker/download.sh && \
		sed -i 's/\r$//' /workspace/Docker/download.sh && \
		sed -i 's/\r$//' /workspace/Docker/links.txt && \
		sed -i 's/\r$//' /workspace/Docker/links.sha256 && \
		/workspace/Docker/download.sh && \
        python /workspace/Docker/download.py && \
        python -m nltk.downloader averaged_perceptron_tagger cmudict; \
    fi

# 第二阶段：最终应用构建
FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04

LABEL maintainer="breakstring@hotmail.com"
LABEL version="dev-20240209"
LABEL description="Docker image for GPT-SoVITS"

# 安装ffmpeg和其他必要的依赖
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ffmpeg libsox-dev libjpeg-dev libpng-dev parallel aria2 git git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# 复制第一阶段构建的结果
COPY --from=builder /workspace /workspace

# 从builder阶段复制已安装的Python依赖
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the rest of the application
COPY . /workspace

EXPOSE 5006 5007 5008

CMD ["python", "api_run.py"]