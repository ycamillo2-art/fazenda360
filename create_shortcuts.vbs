Set oWS = WScript.CreateObject("WScript.Shell")
pythonPath = "C:\Users\YAGOCAMILLO\AppData\Roaming\Accio\pre-install\python\python.exe"
projectPath = "C:\Users\YAGOCAMILLO\.accio\accounts\1759546559\agents\DID-F456DA-42F456DAU1777741-8451-8270FF\project"

sLinkFile2 = oWS.SpecialFolders("Desktop") & "\INICIAR FAZENDA360.lnk"
Set oLink2 = oWS.CreateShortcut(sLinkFile2)
oLink2.TargetPath = "cmd.exe"
oLink2.Arguments = "/k ""cd /d " & projectPath & " && " & """" & pythonPath & """" & " manage.py runserver 0.0.0.0:8000"""
oLink2.Description = "Inicia o servidor Fazenda360"
oLink2.Save
