@echo off
REM 输出构建信息
echo Building your application...

REM 设置虚拟环境
if exist .venv (
    echo Virtual environment already exists.
) else (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created.
)

REM 激活虚拟环境
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM 测试 Python 环境
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM 安装依赖
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Please check your requirements.txt file and try again.
    exit /b 1
)
echo Dependencies installed.

REM 打包应用程序
echo Packaging application...
rmdir /s /q build
rmdir /s /q dist
python -m PyInstaller main.spec
if %ERRORLEVEL% NEQ 0 (
    echo Failed to package application. Please check your main.py file and try again.
    exit /b 1
)
echo Application packaged.
