import subprocess
import os
import sys

print("=" * 60)
print("压缩超大视频工具")
print("=" * 60)
print()

input_video = r"D:\AcerAI\facefusion\facefusion\out\b7de99dc.mp4"
output_video = "压缩_output.mp4"

print(f"输入: {input_video}")
print(f"输出: {output_video}")
print()

# 检查文件是否存在
if not os.path.exists(input_video):
    print("[错误] 输入文件不存在")
    sys.exit(1)

# 获取原始文件大小
input_size = os.path.getsize(input_video)
print(f"原始大小: {input_size:,} 字节 ({input_size / (1024**3):.2f} GB)")
print()

print("[提示] 正在压缩，这可能需要一些时间...")
print()

# FFmpeg 命令
cmd = [
    "ffmpeg",
    "-i", input_video,
    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",
    "-c:a", "aac",
    "-b:a", "192k",
    "-y",
    output_video
]

try:
    result = subprocess.run(cmd, check=True)
    
    if os.path.exists(output_video):
        output_size = os.path.getsize(output_video)
        print()
        print("=" * 60)
        print("[成功] 视频已压缩！")
        print("=" * 60)
        print(f"输出文件: {output_video}")
        print(f"压缩后大小: {output_size:,} 字节 ({output_size / (1024**3):.2f} GB)")
        print(f"压缩率: {(1 - output_size/input_size) * 100:.1f}%")
    else:
        print("[错误] 输出文件未生成")
        
except subprocess.CalledProcessError as e:
    print(f"[错误] 压缩失败: {e}")
except Exception as e:
    print(f"[错误] {e}")

print()
input("按回车键退出...")
