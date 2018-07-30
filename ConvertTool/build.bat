@echo off

serverbin\dist\ConvertTool.exe -f  ≤∂”„≈‰÷√±Ì.xlsx -t server
serverbin\dist\ConvertTool.exe -f  ≤∂”„≈‰÷√±Ì.xlsx -t client
serverbin\dist\MergeConfig.exe -f  server\ -t server\Config.zip

pause