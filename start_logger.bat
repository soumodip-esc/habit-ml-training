@echo off
cd C:\lab_agent
call myenv\Scripts\activate
echo boot > boot_flag.txt
pythonw logger.py