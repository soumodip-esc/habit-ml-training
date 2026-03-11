@echo off
cd your folders path not files eg C:\Users\YourName\Documents\Projects
call myenv\Scripts\activate
echo boot > boot_flag.txt
pythonw logger.py