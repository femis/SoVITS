# coding=utf-8
from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config
import soundfile as sf
import argparse
import time
from datetime import datetime

def get_time():
    # 打印格式化的当前日期和时间
    formatted_now = datetime.now().strftime("%Y年%m月%d日 %H时%M分%S秒")
    return formatted_now

def tts_handle(req: dict):
    # 打印传入的配置信息
    print(f"传入的配置是: {req}")
    print(f"即将开始制作，当前时间：{get_time()}")
    # 保存到本地的音频
    output_file = req.get("output_file", "generated_audio.wav")
    # 从传入的配置中获取所需的媒体类型，若未提供则默认为wav格式
    media_type = req.get("media_type", "wav")
    # 从传入的配置中获取TTS推理配置文件的路径，若未提供则默认为"GPT_SoVITS/configs/tts_infer.yaml"
    tts_infer_yaml_path = req.get("tts_infer_yaml_path", "GPT_SoVITS/configs/tts_infer.yaml")
    # 根据提供的配置文件路径创建TTS配置对象
    tts_config = TTS_Config(tts_infer_yaml_path)

    try:
        # 使用创建的TTS配置对象初始化TTS类的实例
        tts_instance = TTS(tts_config)
        # 使用初始化的TTS实例处理输入请求，生成音频数据
        tts_generator = tts_instance.run(req)
        # 获取生成的音频数据和采样率
        sr, audio_data = next(tts_generator)
        # 保存音频到本地文件
        sf.write(output_file, audio_data, sr)
        print(f"音频已保存到: {output_file}")
        # 清理缓存
        tts_instance.empty_cache()
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
def main():
    start_time = time.time()
    print(f"收到制作请求，当前时间：{get_time()}")
    parser = argparse.ArgumentParser(description='文字转语言服务')
    parser.add_argument('--text', type=str, default ="早知他来，我就不来了", help='输入文字')
    parser.add_argument('--ref_audio_path', type=str, default='example/model-dali.mp3', help='参考音频')
    parser.add_argument('--prompt_text', type=str, default='我叫夯大力,我以为上了大学就不会有调休的说法,要不是周六要上周五的课,我差点就信了', help='参考音频文案')
    parser.add_argument('--text_split_method', type=str, default='cut2', help='切割方式')
    parser.add_argument('--speed_factor', type=str, default='1.15', help='语速')
    parser.add_argument('--output_file', type=str, default='generated_audio.wav', help='输出文件')
    parser.add_argument('--yaml_path', type=str, default='GPT_SoVITS/configs/tts_infer.yaml', help='配置文件')
    # 添加更多参数...
    args = parser.parse_args()
    result = tts_handle({
        "text": args.text,  # 待合成的文本内容
        "text_lang": "zh",  # 待合成文本的语言。
        "ref_audio_path": args.ref_audio_path,  # 参考音频的路径。
        "aux_ref_audio_paths": [],  # 辅助参考音频路径列
        "prompt_text": args.prompt_text,  # 参考音频的提示文本
        "prompt_lang": "zh",  # 参考音频提示文本的语言。
        "top_k": 5,  # 顶K采样值，用于控制生成文本的多样性。
        "top_p": 1,  # 顶P采样值，同样用于控制生成文本的多样性。
        "temperature": 1,  # 采样时的温度参数，影响生成的随机性。
        "text_split_method": args.text_split_method,  # 文本分割方法
        "output_file": args.output_file,  # 保存到本地的文件
        "batch_size": 20,  # 推理时的批量大小。
        "batch_threshold": 1,  # 批量分割的阈值。
        "speed_factor": float(args.speed_factor),  # 控制合成音频的播放速度。。
        "split_bucket": True,  # 是是否将批量数据分割成多个桶进行处理。
        "fragment_interval": 0.3,  # 控制音频片段的间隔时间。 。
        "seed": 2381411557,  # 随机种子，用于保证结果的可复现性。
        "media_type": "wav",
        "streaming_mode": False,
        "parallel_infer": True,  # 是否使用并行推理。
        "repetition_penalty": 1.35,  # T2S模型中的重复惩罚参数，用于减少文本中重复词语的生成。
        "tts_infer_yaml_path": args.yaml_path
    })
    end_time = time.time()
    print(f"制作请求完成; 耗时：{end_time-start_time}秒，当前时间：{get_time()}")
    print(f"生成结果: 【:{result}:】")

if __name__ == '__main__':
    main()