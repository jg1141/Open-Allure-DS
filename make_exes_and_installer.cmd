echo off
rem 20111206 JG Modified to run for SlideSpeech and SlideSpeech Converter
echo ========================
echo Building SlideSpeech.exe
echo ========================
cd wikitospeech
if exist dist (rmdir dist /S)
if exist build (rmdir build /S)
python exeMaker.py py2exe
cd ..\odp2wts
echo =================================
echo Building SlideSpeechConverter.exe
echo =================================
if exist dist (rmdir dist /S)
python exeMaker.py py2exe
cd ..
D:\NSIS\makensisw.exe SlideSpeechInstaller.nsi
