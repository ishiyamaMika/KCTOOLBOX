@echo off
setx KEICA_TOOL_PATH %~dp0


set /P _KCUSERNAME_="���[�U�[��(shotgun�̃A�J�E���g�� like: Taro.Yamada): " 
echo %_KCUSERNAME_%

setx KEICA_USERNAME %_KCUSERNAME_%
echo ���ϐ�KEICA_TOOL_PATH��%KEICA_TOOL_PATH%�ɐݒ肵�܂���
echo ���ϐ�KEICA_USERNAME��%_KCUSERNAME_%�ɐݒ肵�܂���

pause