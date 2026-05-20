Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /k cd C:\Users\bloon\Downloads\huayen\editor && npm run dev", 1, False
WScript.Sleep 3000
WshShell.Run "http://localhost:5173/", 1, False