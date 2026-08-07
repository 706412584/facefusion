import subprocess
import os

print("=" * 60)
print("修复损坏的视频文件")
print("=" * 60)
print()

input_video = r"D:\AcerAI\facefusion\facefusion\out\b7de99dc.mp4"
output_video = "修复_output.mp4"

print(f"输入: {input_video}")
print(f"输出: {output_video}")
print()

if not os.path.exists(input_video):
    print("[错误] 输入文件不存在")
    exit(1)

print("[提示] 正在尝试修复视频...")
print()

# 尝试修复 moov atom
cmd = [
    "ffmpeg",
    "-err_detect", "ignore_err",
    "-i", input_video,
    "-c", "copy",
    "-movflags", "faststart",
    "-y",
    output_video
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(output_video) and os.path.getsize(output_video) > 0:
        print()
        print("=" * 60)
        print("[成功] 视频已修复！")
        print("=" * 60)
        print(f"输出文件: {output_video}")
        print(f"大小: {os.path.getsize(output_video):,} 字节")
    else:
        print("[错误] 修复失败，文件可能无法恢复")
        print()
        print("建议：重新处理原视频")
        
except Exception as e:
    print(f"[错误] {e}")

print()
input("按回车键退出...")
