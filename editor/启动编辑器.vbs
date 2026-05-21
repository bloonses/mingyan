Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = WshShell.ExpandEnvironmentStrings("%~dp0")
WshShell.Run "cmd /k cd /d %~dp0 && npm run dev", 1, False
WScript.Sleep 3000
WshShell.Run "http://localhost:5173/", 1, False
