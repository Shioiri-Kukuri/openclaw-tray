Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "E:\BaiduSyncdisk\KnowledgeBase\LLM\Project\openclaw-tray"
WshShell.Run "pythonw main.py", 0, False
