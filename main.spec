# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 这里的 a 是分析你的代码的对象
a = Analysis(
    ['main.py'],  # 主程序
    pathex=['./'],  # 项目路径
    binaries=[],  # 可执行二进制文件，留空即可
    # 包含所有模块和资源
    datas=[
        ('./app/*', 'app'),
        ('./core/*', 'core'),
    ],
    hiddenimports=[],  # 如果有隐藏的依赖，可以在这里添加
    hookspath=[],  # 自定义 hook 文件的路径，通常不用修改
    runtime_hooks=[],  # 运行时的 hook 脚本
    excludes=[]  # 如果有不需要的模块，可以在这里排除
)

# 生成 pyz 文件
pyz = PYZ(a.pure)

# EXE 是最终生成的可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,  # 打包时的所有数据（包括模块和资源）
    name='ImageUtils',  # 生成的可执行文件名称
    debug=False,
    strip=False,
    upx=True,
    console=False,  # 是否在命令行窗口中运行
    icon='icon.ico'
)
