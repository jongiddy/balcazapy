@echo off

%= Run this batch script from the top-level of the Balcazapy installation. =%
%= Edit the following line to the correct value, and add the bin folder    =%
%= to your PATH. =%
set PYTHON_HOME=C:\Python27

for %%f in ("%CD%") do @set BALCAZAPY_HOME=%%~sf

set BALC="bin\balc.bat"

del /q %BALC%
rmdir /q bin
mkdir bin

echo @echo off> %BALC%
echo set PYTHON=%PYTHON_HOME%\python>> %BALC%
echo set BALCAZAPY_HOME=%BALCAZAPY_HOME%>> %BALC%
echo set BALCAZAPROG=%%0>> %BALC%
echo set PYTHONPATH=%%BALCAZAPY_HOME%%\python>> %BALC%
echo "%%PYTHON%%" -m balcaza.T2FlowBuilder %%*>> %BALC%
