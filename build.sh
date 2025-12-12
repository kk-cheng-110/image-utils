#!/bin/bash

echo "Building your application..."

# 设置虚拟环境
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python -m venv .venv
  echo "Virtual environment created."
else
  echo "Virtual environment already exists."
fi

# 激活虚拟环境
echo "Activating virtual environment..."
source .venv/bin/activate

# 测试 Python 环境
if ! python --version; then
  echo "Python is not installed. Please install Python and try again."
  exit 1
fi

# 安装依赖
echo "Installing dependencies..."
if ! pip install -r requirements.txt; then
  echo "Failed to install dependencies. Please check your requirements.txt file and try again."
  exit 1
fi
echo "Dependencies installed."

# 打包应用程序
echo "Packaging application..."
rm -rf build dist
if ! python -m PyInstaller main.spec; then
  echo "Failed to package application. Please check your main.py file and try again."
  exit 1
fi
echo "Application packaged."
