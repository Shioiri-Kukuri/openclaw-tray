@echo off
cd /d "%~dp0"
set OPENCLAW_CONFIG_PATH=C:\Users\zhangjiete\.openclaw-instance2\openclaw.json
set OPENCLAW_STATE_DIR=C:\Users\zhangjiete\.openclaw-instance2
start "OpenClaw Instance 2" /min openclaw gateway --port 18790
echo OpenClaw Instance 2 started on port 18790
