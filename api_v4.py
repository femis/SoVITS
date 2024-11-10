# coding=utf-8
from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config
import soundfile as sf
from flask import Flask, request, jsonify
import time
from datetime import datetime
import argparse
app = Flask(__name__)
parser = argparse.ArgumentParser(description='文字转语言服务')

tts_config_cache = {}  # 缓存 TTS_Config 对象
tts_init_cache = {}
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

# 初始化TTs方法
def tts_handle(req: dict):
    # 打印传入的配置信息
    print(f"传入的配置是: {req}")
    # 保存到本地的音频
    output_file = req.get("output_file", "generated_audio.wav")

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

        return {
            "path": output_file,
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
def get_time():
    # 打印格式化的当前日期和时间
    formatted_now = datetime.now().strftime("%Y年%m月%d日 %H时%M分%S秒")
    return formatted_now
@app.route('/', methods=['GET','POST'])
def hello():
    start_time = time.time()
    print(f"即将开始制作，当前时间：{get_time()}")
    json = request.json
    text = json.get('text', '早知他来，我就不来了')
    ref_audio_path = json.get('ref_audio_path', 'example/model-dali.mp3')
    prompt_text = json.get('prompt_text', '')
    aux_ref_audio = json.get('aux_ref_audio', [])
    text_split_method = json.get('text_split_method', 'cut2')
    speed_factor = json.get('speed_factor', 1.15)
    output_file = json.get('output_file', 'generated_audio.wav')
    yaml_path = json.get('yaml_path', 'GPT_SoVITS/configs/daiyu.yaml')
    unique_id = json.get('unique_id', '123456')
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
        "batch_size": 20,  # 推理时的批量大小。
        "batch_threshold": 1,  # 批量分割的阈值。
        "speed_factor": float(speed_factor),  # 控制合成音频的播放速度。。
        "split_bucket": True,  # 是是否将批量数据分割成多个桶进行处理。
        "fragment_interval": 0.3,  # 控制音频片段的间隔时间。 。
        "seed": -1,  # 随机种子，用于保证结果的可复现性。
        "media_type": "wav",
        "streaming_mode": False,
        "parallel_infer": True,  # 是否使用并行推理。
        "repetition_penalty": 1.35,  # T2S模型中的重复惩罚参数，用于减少文本中重复词语的生成。
        "tts_infer_yaml_path": yaml_path,
        "unique_id": unique_id
    })
    end_time = time.time()
    print(f"制作请求完成; 耗时：{end_time - start_time}秒，当前时间：{get_time()}")
    print(f"生成结果: {result}")
    return jsonify(result)

if __name__ == '__main__':
    parser.add_argument('--port', type=str, default="5101", help='输入端口号')
    args = parser.parse_args()
    app.run(debug=False, host="0.0.0.0", port=args.port)
