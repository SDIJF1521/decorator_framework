#!/usr/bin/env python3
"""
自动上传脚本 - 用于将包上传到PyPI
使用前请确保已安装：pip install twine build
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """运行命令并检查返回码"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误信息: {e.stderr}")
        return False

def check_setup():
    """检查setup.py中的必要配置"""
    setup_file = Path("setup.py")
    if not setup_file.exists():
        print("❌ setup.py文件不存在")
        return False
    
    content = setup_file.read_text(encoding='utf-8')
    
    # 检查必要的字段
    required_fields = [
        'name="decorator-framework"',
        'version=',
        'author=',
        'author_email=',
        'description=',
        'url=',
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in content:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"⚠️  setup.py中缺少以下字段: {', '.join(missing_fields)}")
        print("请在继续之前更新setup.py文件")
        return False
    
    print("✅ setup.py配置检查通过")
    return True

def main():
    """主函数"""
    print("🚀 开始PyPI上传流程...")
    
    # 步骤1: 检查setup.py
    if not check_setup():
        return False
    
    # 步骤2: 清理旧的构建文件
    print("\n🧹 清理旧的构建文件...")
    for folder in ['build', 'dist', '*.egg-info']:
        if os.path.exists(folder):
            import shutil
            shutil.rmtree(folder)
            print(f"已删除: {folder}")
    
    # 步骤3: 构建包
    if not run_command("python -m build", "构建包"):
        return False
    
    # 步骤4: 检查包
    if not run_command("twine check dist/*", "检查包"):
        return False
    
    # 步骤5: 询问用户选择上传目标
    print("\n📤 选择上传目标:")
    print("1. 测试PyPI (test.pypi.org)")
    print("2. 正式PyPI (pypi.org)")
    print("3. 取消上传")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice == '1':
        # 上传到测试PyPI
        if run_command("twine upload --repository testpypi dist/*", "上传到测试PyPI"):
            print("\n🎉 包已成功上传到测试PyPI!")
            print("你可以在 https://test.pypi.org/project/decorator-framework/ 查看")
            print("测试安装命令: pip install --index-url https://test.pypi.org/simple/ decorator-framework")
            return True
    elif choice == '2':
        # 上传到正式PyPI
        if run_command("twine upload dist/*", "上传到正式PyPI"):
            print("\n🎉 包已成功上传到正式PyPI!")
            print("你可以在 https://pypi.org/project/decorator-framework/ 查看")
            print("安装命令: pip install decorator-framework")
            return True
    else:
        print("\n❌ 上传已取消")
        return False
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✨ 上传流程完成！")
        else:
            print("\n💥 上传流程失败，请检查错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        sys.exit(1)