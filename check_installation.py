#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 AIStock 系統所需的套件是否已正確安裝
"""

def check_package(package_name, import_name=None):
    """檢查套件是否已安裝"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} - 已安裝")
        return True
    except ImportError:
        print(f"❌ {package_name} - 未安裝")
        return False

def main():
    print("=== AIStock 套件安裝檢查 ===")
    print("檢查系統所需的 Python 套件...\n")
    
    # 需要檢查的套件列表
    packages = [
        ("yfinance", "yfinance"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("ta", "ta"),
        ("scikit-learn", "sklearn"),
        ("plotly", "plotly"),
        ("dash", "dash"),
        ("dash-bootstrap-components", "dash_bootstrap_components"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("schedule", "schedule")
    ]
    
    installed_count = 0
    total_count = len(packages)
    
    for package_name, import_name in packages:
        if check_package(package_name, import_name):
            installed_count += 1
    
    print(f"\n=== 檢查結果 ===")
    print(f"已安裝: {installed_count}/{total_count}")
    print(f"成功率: {installed_count/total_count*100:.1f}%")
    
    if installed_count == total_count:
        print("\n🎉 所有套件都已正確安裝！")
        print("您可以開始使用 AIStock 系統了。")
        print("\n建議執行:")
        print("1. python test_system.py - 測試系統功能")
        print("2. python main.py - 進入互動模式")
        print("3. python main.py AAPL --plot - 分析蘋果股票")
    else:
        print(f"\n⚠️ 還有 {total_count - installed_count} 個套件未安裝")
        print("請執行以下命令安裝缺少的套件:")
        print("pip install -r requirements.txt")
        
        # 顯示缺少的套件
        print("\n缺少的套件:")
        for package_name, import_name in packages:
            try:
                __import__(import_name)
            except ImportError:
                print(f"  - {package_name}")

if __name__ == "__main__":
    main() 