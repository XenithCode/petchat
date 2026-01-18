# 打包指南

## 使用 PyInstaller（推荐）

### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

### 2. 打包客户端

```bash
python -m PyInstaller --name=pet-chat --onefile --windowed main.py
```

### 3. 打包服务器

```bash
python -m PyInstaller --name=pet-chat-server --onefile server.py
```

### 4. 输出

打包完成后，可执行文件位于 `dist/` 目录：
- `dist/pet-chat.exe` - 客户端
- `dist/pet-chat-server.exe` - 服务器

## 使用 Nuitka（可选）

### 1. 安装 Nuitka

```bash
pip install nuitka
```

### 2. 打包

```bash
# 客户端
python -m nuitka --standalone --onefile --windows-disable-console --enable-plugin=pyqt6 main.py

# 服务器
python -m nuitka --standalone --onefile --enable-plugin=pyqt6 server.py
```

## 注意事项

1. **依赖问题**：
   - 确保所有依赖都已安装
   - PyQt6 可能需要额外配置

2. **文件大小**：
   - PyInstaller: 约 50-100MB
   - Nuitka: 约 30-80MB

3. **首次运行**：
   - 打包后的 exe 首次运行可能较慢
   - 需要配置 API Key 才能使用 AI 功能

4. **配置文件**：
   - `config.json` 会在 exe 同目录创建
   - `petchat.db` 会在 exe 同目录创建

## 部署说明

### 服务器部署

1. 将 `pet-chat-server.exe` 部署到服务器
2. 运行服务器，默认监听 `0.0.0.0:8888`
3. 确保防火墙允许 8888 端口的 TCP 连接

### 客户端分发

1. 将 `pet-chat.exe` 分发给用户
2. 用户启动时输入服务器 IP 地址
3. 连接成功后即可开始聊天

## 常见问题

### PyInstaller 打包后无法运行

- 检查是否有缺失的 DLL
- 尝试添加 `--collect-all=PyQt6`
- 临时使用 `--console` 查看错误信息

### Nuitka 打包失败

- 确保安装了 C++ 编译器（Visual Studio Build Tools）
- 尝试使用 `--standalone` 模式
