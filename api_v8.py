# coding=utf-8
import requests
import soundfile as sf
import tempfile
from flask import Flask, request, jsonify, send_file
import time
from datetime import datetime
import argparse
import os
import torch
from pydub import AudioSegment

import sys
import os

# 启用并行推理
os.environ["TOKENIZERS_PARALLELISM"] = "true"  # 或 "true"
# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), './GPT_SoVITS'))
print("追加项目根目录:", project_root)

# 确保项目根目录在 sys.path 中
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config

app = Flask(__name__)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
parser = argparse.ArgumentParser(description='文字转语言服务')
# 获取当前目录 绝对地址
temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TEMP")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('当前使用的设备是：', device)

tts_config_cache = {}  # 缓存 TTS_Config 对象
tts_init_cache = {}
is_makeing = 0         #是否正在制作中


def get_tts_config(req):
    global tts_config_cache  # 使用global声明来访问外部的tts_config_cache
    tts_infer_yaml_path = req.get("tts_infer_yaml_path", "GPT_SoVITS/configs/tts_infer.yaml")
    unique_id = req.get("unique_id", "123456")
    print(f"本地请求的唯一Id: {unique_id}")
    # 检查缓存大小，如果超过20则清空缓存
    if len(tts_config_cache) > 20:
        print("缓存大小超过10，清空缓存...")
        for instance_id, instance in list(tts_config_cache.items()):
            print(f"删除索引： {instance_id}")
            del tts_config_cache[instance_id]

    # 由于我们可能刚清空了缓存，现在再次检查unique_id是否在缓存中
    if unique_id not in tts_config_cache:
        print(f"从文件加载配置并添加到缓存中: {tts_infer_yaml_path}")
        # 假设TTS_Config是一个类，它接受yaml文件路径作为参数来加载配置
        tts_config_cache[unique_id] = TTS_Config(tts_infer_yaml_path)

    # 注意这里应该返回与unique_id关联的配置对象，而不是与tts_infer_yaml_path关联的对象（这可能是一个错误）
    return tts_config_cache[unique_id]

# 加载TTS缓存
def init_tts (req) :
    global tts_init_cache
    unique_id = req.get("unique_id", "123456")
    tts_init_max = req.get("tts_init_max", 5)
    tts_config = get_tts_config(req)
    print(f"将TTS实例当前已存储： {len(tts_init_cache)}， 最大允许： {tts_init_max} 条")
    if len(tts_init_cache) > tts_init_max:
        print(f"初始化TTS超过{tts_init_max}，清空缓存中...")
        for instance_id, instance in list(tts_init_cache.items()):
            # 需要清理释放缓/
            instance.stop()
            instance.empty_cache()
            print(f"删除索引： {instance_id}")
            del tts_init_cache[instance_id]

    if unique_id not in tts_init_cache:
        print(f"将TTS实例增加到缓存中...{unique_id}")
        # 假设TTS_Config是一个类，它接受yaml文件路径作为参数来加载配置
        tts_init_cache[unique_id] = TTS(tts_config)

    return tts_init_cache[unique_id]

# 下载文件
def download_file(url:str = ''):
    # 判断文件是 http 开头才执行, 否则直接返回
    if not url.startswith('http'):
        return url
    # 发送GET请求
    try:
        response = requests.get(url)
        # 确保请求成功
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir=temp_dir) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name  # 获取临时文件的路径
            print(f'文件已成功下载到系统缓存目录: {temp_file_path}')
            return temp_file_path
        else:
            print('下载失败，状态码:', response.status_code)
            return ""
    except Exception as e:
        print('下载失败')
        return ""

# 将mp3转wav
def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    # 加载MP3文件
    audio = AudioSegment.from_mp3(mp3_file_path)
    # 导出为WAV文件
    audio.export(wav_file_path, format="wav")
    print('转WAV成功', wav_file_path)
    return wav_file_path

# 将wav转mp3
def convert_wav_to_mp3(wav_file_path, mp3_file_path ):
    # 加载WAV文件
    wav_file = AudioSegment.from_wav(wav_file_path)
    # 导出为MP3文件
    wav_file.export(mp3_file_path, format="mp3")
    return mp3_file_path

# 获取临时文件
def get_temp_file(ext:str = '.mp3'):
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=temp_dir).name
    print(f"临时文件路径: {output_file}")
    return output_file

# 初始化TTs方法
def tts_handle(req: dict):
    # 打印传入的配置信息
    print(f"传入的配置是: {req}")
    # 保存到本地的音频
    output_file = get_temp_file()

    try:
        # 使用创建的TTS配置对象初始化TTS类的实例
        tts_instance = init_tts(req)
        # 使用初始化的TTS实例处理输入请求，生成音频数据
        tts_generator = tts_instance.run(req)
        # 获取生成的音频数据和采样率
        sr, audio_data = next(tts_generator)
        # 保存音频到本地文件
        sf.write(output_file, audio_data, sr)
        print(f"音频已保存到: {output_file}")
        file_name = os.path.basename(output_file)
        return {
            "path": output_file,
            'name': file_name,
            "success": 1,
            "msg": "制作成功!"
        }
    except Exception as e:
        # 如果在处理请求过程中发生异常，打印错误信息并返回一个空响应对象
        print(f"生成失败: {str(e)}")
        return {
            "path": output_file,
            "success": 0,
            "msg": str(e)
        }
# 获取当前时间
def get_time():
    # 打印格式化的当前日期和时间
    formatted_now = datetime.now().strftime("%Y年%m月%d日 %H时%M分%S秒")
    return formatted_now
@app.route('/make', methods=['POST'])
def enter():
    global is_makeing
    start_time = time.time()
    is_makeing = 1
    print(f"即将开始制作，当前时间：{get_time()}")

    json = request.json
    text = json.get('text', '早知他来，我就不来了')

    ref_audio_path_url = json.get('ref_audio_path', 'https://vr-static.he29.com/public/case/rabbit/model-baijing.mp3')
    ref_audio_path = download_file(ref_audio_path_url)

    prompt_text = json.get('prompt_text', '')
    aux_ref_audio_list = json.get('aux_ref_audio', [])
    aux_ref_audio = []
    # 循环下载 aux_ref_audio 里面的音频
    aux_ref_audio = [download_file(url) for url in aux_ref_audio_list]

    text_split_method = json.get('text_split_method', 'cut2')
    speed_factor = json.get('speed_factor', 1)

    # 下载文件
    output_file = get_temp_file()
    yaml_path = json.get('yaml_path', 'GPT_SoVITS/configs/daiyu.yaml')
    unique_id = json.get('unique_id', '123456')
    seed = json.get('seed', -1)
    batch_size = json.get('batch_size',20) # 批次大小
    tts_init_max = json.get('tts_init_max', 5) # 最大缓存个数;
    result = tts_handle({
        "text": text,  # 待合成的文本内容
        "text_lang": "zh",  # 待合成文本的语言。
        "ref_audio_path": ref_audio_path,  # 参考音频的路径。
        "aux_ref_audio_paths": aux_ref_audio,  # 辅助参考音频路径列
        "prompt_text": prompt_text,  # 参考音频的提示文本
        "prompt_lang": "zh",  # 参考音频提示文本的语言。
        "top_k": 5,  # 顶K采样值，用于控制生成文本的多样性。
        "top_p": 1,  # 顶P采样值，同样用于控制生成文本的多样性。
        "temperature": 1,  # 采样时的温度参数，影响生成的随机性。
        "text_split_method": text_split_method,  # 文本分割方法
        "output_file": output_file,  # 保存到本地的文件
        "batch_size": int(batch_size),  # 推理时的批量大小。
        "batch_threshold": 1,  # 批量分割的阈值。
        "speed_factor": float(speed_factor),  # 控制合成音频的播放速度。。
        "split_bucket": True,  # 是是否将批量数据分割成多个桶进行处理。
        "fragment_interval": 0.3,  # 控制音频片段的间隔时间。 。
        "seed": int(seed),  # 随机种子，用于保证结果的可复现性。
        "media_type": "wav",
        "streaming_mode": False,
        "parallel_infer": True,  # 是否使用并行推理。
        "repetition_penalty": 1.35,  # T2S模型中的重复惩罚参数，用于减少文本中重复词语的生成。
        "tts_infer_yaml_path": yaml_path,
        "unique_id": unique_id,
        "tts_init_max": int(tts_init_max)
    })
    end_time = time.time()
    print(f"制作请求完成; 耗时：{end_time - start_time}秒，当前时间：{get_time()}")
    print(f"生成结果: {result}")
    is_makeing = 0
    return jsonify(result)

# 下载文件
@app.route('/download', methods=['GET'])
def download():
    # 从GET请求获取文件路径
    file_path = request.args.get('path', '')
    try:
        # 检查路径是否包含 TEMP
        if 'TEMP' in file_path:
            # 截取 TEMP 后面的部分
            relative_path = file_path.split('TEMP', 1)[1].lstrip(os.sep)
            # 构建完整的路径
            full_path = os.path.join(PROJECT_ROOT, 'TEMP', relative_path)
        else:
            # 直接使用传递的相对路径
            full_path = os.path.join(PROJECT_ROOT, 'TEMP', file_path)
        # 文件不存在就返回404
        if not os.path.exists(full_path):
            return jsonify({'error': '文件不存在'}), 404
        # 从本地读取文件并且输出
        return send_file(full_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def find():
    try:
        # 获取个数及名字
        tts_len = len(tts_init_cache)
        tts_len_keys = tts_init_cache.keys()
        config_len = len(tts_config_cache)
        config_len_keys = tts_config_cache.keys()
        result = {
            'tts_len' : {
                'count' : tts_len,
                'list' : list(tts_len_keys)
            },      # 实例的个数
            'config_len': {
                'count': config_len,
                'list':  list(config_len_keys)
            }, # 配置文件个数
            'is_makeing': is_makeing  # 是否制作中
        }
        print(f"查询结果: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"处理 / 请求时发生异常: {e}")  # 记录异常信息
        return jsonify({"error": "处理请求时发生内部错误"}), 500  # 返回错误响应

if __name__ == '__main__':
    parser.add_argument('--port', type=str, default="5403", help='输入端口号')
    args = parser.parse_args()
    app.run(debug=False, host="0.0.0.0", port=args.port)
