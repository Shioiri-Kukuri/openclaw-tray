# OpenClay Tray

轻量级系统托盘应用，用于管理 OpenClaw Gateway 服务。

## 功能

- 系统托盘图标显示服务状态
- 右键菜单：启动/停止/重启服务
- 快速打开 Dashboard
- 开机自启（可选）

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

## 开机自启

将 `openclaw-tray.bat` 的快捷方式放入 Windows 启动文件夹：
- `Win+R` → 输入 `shell:startup` → 回车
- 将快捷方式放入打开的文件夹

## 依赖

- Python 3.8+
- pystray
- Pillow
- psutil
