import torch

# 检查CUDA是否可用
print(f"Is CUDA available: {torch.cuda.is_available()}")

# 获取CUDA版本
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"PyTorch Version: {torch.__version__}")

    # 获取当前设备信息
    current_device = torch.cuda.current_device()
    print(f"Current CUDA Device: {current_device}")
    print(f"Device Name: {torch.cuda.get_device_name(current_device)}")
else:
    print("CUDA is not available.")