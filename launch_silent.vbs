Set WshShell = CreateObject("WScript.Shell")
Dim strCurDir
strCurDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strCurDir
WshShell.Run """" & strCurDir & "\.venv\Scripts\pythonw.exe"" """ & strCurDir & "\main.py""", 0, False
Set WshShell = Nothing
