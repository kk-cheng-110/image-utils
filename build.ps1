# 输出构建信息
Write-Host "Building your application..."

Write-Host "[Step1]开始设置虚拟环境..."
# 设置虚拟环境
$envPath = ".venv"
if (Test-Path $envPath)
{
    Write-Host "Virtual environment already exists."
}
else
{
    Write-Host "Creating virtual environment..."
    python -m venv $envPath
    Write-Host "Virtual environment created."
}

# 激活虚拟环境
. "$envPath\Scripts\Activate.ps1"

# 测试 Python 环境
$pythonVersion = python --version
if ($LASTEXITCODE -ne 0)
{
    Write-Host "Python is not installed. Please install Python and try again."
    exit 1
}
Write-Host "[Step1]虚拟环境设置完成."

# 安装依赖
Write-Host "[Step2]开始安装依赖..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0)
{
    Write-Host "Failed to install dependencies. Please check your requirements.txt file and try again."
    exit 1
}
Write-Host "[Step2]依赖安装完成."

# 打包应用程序
Write-Host "[Step3]开始打包应用程序..."
Remove-Item -Recurse -Force build, dist
python -m PyInstaller main.spec
if ($LASTEXITCODE -ne 0)
{
    Write-Host "Failed to package application. Please check your main.py file and try again."
    exit 1
}
Write-Host "[Step3]打包应用程序完成,已输出至 dist 目录."
