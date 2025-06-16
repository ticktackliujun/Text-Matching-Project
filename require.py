import sys
from importlib import util

# 检查Python版本
if sys.version_info < (3, 6):
    print("错误：需要Python 3.6或更高版本")
    sys.exit(1)

# 检查依赖库
required_packages = ["PyQt5", "matplotlib"]
missing = []

for pkg in required_packages:
    if not util.find_spec(pkg):
        missing.append(pkg)

if missing:
    print(f"错误：缺少依赖库：{', '.join(missing)}")
    print("请使用 pip install " + " ".join(missing))
    sys.exit(1)

print("环境检测通过！")