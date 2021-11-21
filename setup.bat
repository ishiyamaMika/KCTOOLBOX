@echo off
setx KEICA_TOOL_PATH %~dp0


set /P _KCUSERNAME_="ユーザー名(shotgunのアカウント名 like: Taro.Yamada): " 
echo %_KCUSERNAME_%

setx KEICA_USERNAME %_KCUSERNAME_%
echo 環境変数KEICA_TOOL_PATHを%KEICA_TOOL_PATH%に設定しました
echo 環境変数KEICA_USERNAMEを%_KCUSERNAME_%に設定しました

pause