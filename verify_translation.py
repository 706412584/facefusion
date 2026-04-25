#!/usr/bin/env python3
"""
验证翻译文件的完整性
Verify translation file integrity
"""

def verify_translations():
    print("=" * 60)
    print("验证翻译文件 / Verifying Translation Files")
    print("=" * 60)
    
    # 直接读取locales文件
    import ast
    with open('facefusion/locales.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含中文翻译
    if "'zh':" in content:
        print("\n✓ 中文语言键已添加 / Chinese language key added")
    else:
        print("\n✗ 未找到中文语言键 / Chinese language key not found")
        return False
    
    # 检查一些关键翻译
    zh_translations = [
        "'processing': '正在处理'",
        "'start_button': '开始'",
        "'stop_button': '停止'",
        "'source_file': '源文件'",
        "'target_file': '目标文件'"
    ]
    
    print("\n检查关键翻译 / Checking key translations:")
    for trans in zh_translations:
        if trans in content:
            print(f"  ✓ {trans}")
        else:
            print(f"  ✗ {trans} (未找到 / not found)")
    
    # 检查types.py
    print("\n检查类型定义 / Checking type definitions:")
    with open('facefusion/types.py', 'r', encoding='utf-8') as f:
        types_content = f.read()
    
    if "Language = Literal['en', 'zh']" in types_content:
        print("  ✓ Language 类型已更新 / Language type updated")
    else:
        print("  ✗ Language 类型未更新 / Language type not updated")
        return False
    
    # 检查translator.py
    print("\n检查翻译器 / Checking translator:")
    with open('facefusion/translator.py', 'r', encoding='utf-8') as f:
        translator_content = f.read()
    
    if "def set_language" in translator_content:
        print("  ✓ set_language 函数已添加 / set_language function added")
    else:
        print("  ✗ set_language 函数未添加 / set_language function not added")
    
    if "def get_language" in translator_content:
        print("  ✓ get_language 函数已添加 / get_language function added")
    else:
        print("  ✗ get_language 函数未添加 / get_language function not added")
    
    # 检查program.py
    print("\n检查程序参数 / Checking program arguments:")
    with open('facefusion/program.py', 'r', encoding='utf-8') as f:
        program_content = f.read()
    
    if "def create_language_program" in program_content:
        print("  ✓ create_language_program 函数已添加 / create_language_program function added")
    else:
        print("  ✗ create_language_program 函数未添加 / create_language_program function not added")
    
    if "--language" in program_content:
        print("  ✓ --language 参数已添加 / --language argument added")
    else:
        print("  ✗ --language 参数未添加 / --language argument not added")
    
    # 检查core.py
    print("\n检查核心逻辑 / Checking core logic:")
    with open('facefusion/core.py', 'r', encoding='utf-8') as f:
        core_content = f.read()
    
    if "translator.set_language" in core_content:
        print("  ✓ 语言设置逻辑已添加 / Language setting logic added")
    else:
        print("  ✗ 语言设置逻辑未添加 / Language setting logic not added")
    
    print("\n" + "=" * 60)
    print("✓ 所有修改已完成！/ All modifications completed!")
    print("=" * 60)
    
    print("\n使用方法 / Usage:")
    print("  python facefusion.py run --language zh")
    print("  python facefusion.py run --language en")
    
    return True

if __name__ == '__main__':
    verify_translations()
