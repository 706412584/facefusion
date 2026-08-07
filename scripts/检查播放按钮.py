#!/usr/bin/env python3
"""检查播放预览按钮是否正确添加"""

print("=" * 60)
print("检查播放预览功能")
print("=" * 60)
print()

# 检查 preview_options.py
print("[1/3] 检查 preview_options.py...")
try:
    with open('facefusion/uis/components/preview_options.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'PREVIEW_PLAY_BUTTON' in content:
            print("✓ PREVIEW_PLAY_BUTTON 已定义")
        else:
            print("✗ PREVIEW_PLAY_BUTTON 未找到")
        
        if 'PREVIEW_SPEED_SLIDER' in content:
            print("✓ PREVIEW_SPEED_SLIDER 已定义")
        else:
            print("✗ PREVIEW_SPEED_SLIDER 未找到")
        
        if '播放预览' in content:
            print("✓ 播放按钮文本已添加")
        else:
            print("✗ 播放按钮文本未找到")
except Exception as e:
    print(f"✗ 错误: {e}")

print()

# 检查 preview.py
print("[2/3] 检查 preview.py...")
try:
    with open('facefusion/uis/components/preview.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'def play_preview' in content:
            print("✓ play_preview 函数已定义")
        else:
            print("✗ play_preview 函数未找到")
        
        if 'preview_play_button' in content:
            print("✓ 播放按钮监听器已添加")
        else:
            print("✗ 播放按钮监听器未找到")
        
        if 'PREVIEW_PLAYING' in content:
            print("✓ 播放状态变量已定义")
        else:
            print("✗ 播放状态变量未找到")
except Exception as e:
    print(f"✗ 错误: {e}")

print()

# 测试导入
print("[3/3] 测试模块导入...")
try:
    from facefusion.uis.components import preview_options
    print("✓ preview_options 模块导入成功")
    
    from facefusion.uis.components import preview
    print("✓ preview 模块导入成功")
    
    print()
    print("=" * 60)
    print("检查完成！")
    print("=" * 60)
    print()
    print("如果所有检查都通过，播放按钮应该在界面上。")
    print("请确保：")
    print("1. 已加载视频文件（不是图片）")
    print("2. 在右侧找到'预览选项'区域")
    print("3. 向下滚动查看播放按钮")
    
except Exception as e:
    print(f"✗ 导入错误: {e}")
    import traceback
    traceback.print_exc()

print()
