@echo off

%= Run this batch script from the top-level of the Balcazapy installation. =%
%= Edit the following lines to the correct values, and add the bin folder  =%
%= to your PATH. =%
set PYTHON_HOME=C:\Python27
set BALCAZAPY_HOME=C:\Users\Ann Other\Desktop\balcazapy

set BALC="bin\balc.bat"

del /q %BALC%
rmdir /q bin
mkdir bin

echo @echo off> %BALC%
echo set PYTHON=%PYTHON_HOME%\python>> %BALC%
echo set BALCAZAPY_HOME=%BALCAZAPY_HOME%>> %BALC%
echo set BALCAZAPROG=%%0>> %BALC%
echo set PYTHONPATH=%CD%\python>> %BALC%
echo "%%PYTHON%%" -m balcaza.T2FlowBuilder %%*>> %BALC%
