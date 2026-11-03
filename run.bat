@echo off
:: Activate the conda environment
CALL C:\Users\peybo\miniconda3\Scripts\activate.bat mt5

:: Run from the repo folder so logs/ and config/ resolve here (not C:\Windows\System32)
cd /d C:\Users\peybo\PycharmProjects\twitter_auto

:: Run the Python script
python C:\Users\peybo\PycharmProjects\twitter_auto\main.py