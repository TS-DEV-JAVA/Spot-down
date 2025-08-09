@echo off
chcp 65001 >nul
color 1                                                          
title Spot-Down Setup
echo Installing Required Stuff...      
pip install rich miniaudio yt-dlp pyaudio keyboard pybase64 ytmusicapi pywebview youtube-search spotipy requests mutagen python-mpv pillow comtypes customtkinter pycaw
rem creat cli-tools folder
if not exist "%~dp0cli-tools" mkdir "%~dp0cli-tools"

rem download it
curl -L -o "%~dp0cli-tools\ffmpeg.exe" "https://github.com/TS-DEV-JAVA/Poke-dl/releases/download/1/ffmpeg.exe"

rem add cli-tools folder to system PATH
setx PATH "%PATH%;%~dp0cli-tools"

rem tell user
echo ffmpeg.exe downloaded to cli-tools and PATH updated.
color a                                                  
echo.                                                                     
echo   _____      __                                                                     
echo  / ___/___  / /___  ______                                            
echo  \__ \/ _ \/ __/ / / / __ \                                          
echo  ___/ /  __/ /_/ /_/ / /_/ / _ _                                    
echo /____/\___/\__/\__,_/ .___(_/_\_/ ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▶   
echo.                                                                                                  ┃
echo                                                                                                   ┃
echo                                                                                                   ┃
echo                                                                                                   ┃
echo                                                                                                   ┃
echo                                                                                                   ┃
echo                                                                              ◀━━━━━━━━━━━━━━━━━━━━┙
echo     ____           __        ____         __                                     ┃
echo    /  _/___  _____/ /_____ _/ / /__  ____/ /                                     ┃
echo    / // __ \/ ___/ __/ __ `/ / / _ \/ __  /                                      ┃
echo  _/ // / / (__  ) /_/ /_/ / / /  __/ /_/ /  ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┙
echo /___/_/ /_/____/\__/\__,_/_/_/\___/\__,_/   
echo.
echo Finished Installing Requirments
echo.     
pause