@echo off

%= Run this batch script from the top-level of the Balcazapy installation. =%
%= Edit the following lines to the correct values, and add the bin folder  =%
%= to your PATH. =%
set PYTHON="C:\Python27\python"

set BALC="bin\balc.bat"

del /q %BALC%
rmdir /q bin
mkdir bin

echo @echo off > %BALC%
echo set PYTHON=%PYTHON% >> %BALC%
echo set PYTHONPATH=%CD%\python >> %BALC%
echo %%PYTHON%% %%* >> %BALC%
