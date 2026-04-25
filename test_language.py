#!/usr/bin/env python3
"""
测试多语言功能
Test language support
"""

def test_languages():
    print("=" * 60)
    print("测试多语言支持 / Testing Language Support")
    print("=" * 60)
    
    # 延迟导入
    import facefusion.translator as translator
    from facefusion.locales import LOCALES
    
    # 测试英文
    print("\n[English Test]")
    translator.set_language('en')
    translator.load(LOCALES, 'facefusion')
    print(f"Language: {translator.get_language()}")
    print(f"Processing: {translator.get('processing')}")
    print(f"Start button: {translator.get('uis.start_button')}")
    
    # 测试中文
    print("\n[中文测试]")
    translator.set_language('zh')
    print(f"语言: {translator.get_language()}")
    print(f"处理中: {translator.get('processing')}")
    print(f"开始按钮: {translator.get('uis.start_button')}")
    
    # 测试更多翻译
    print("\n[更多翻译示例 / More Translation Examples]")
    translator.set_language('en')
    print(f"EN - Processing stopped: {translator.get('processing_stopped')}")
    translator.set_language('zh')
    print(f"ZH - 处理已停止: {translator.get('processing_stopped')}")
    
    translator.set_language('en')
    print(f"EN - Choose image source: {translator.get('choose_image_source')}")
    translator.set_language('zh')
    print(f"ZH - 选择源图像: {translator.get('choose_image_source')}")
    
    print("\n" + "=" * 60)
    print("✓ 多语言测试完成！/ Language test completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_languages()
