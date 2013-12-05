@echo off

%= Run this batch script from the top-level of the Balcazapy installation. =%
%= Edit the following lines to the correct values, and add the bin folder  =%
%= to your PATH. =%
PYTHON="C:\Python27\python"

BALC="bin\balc"

del /q %BALC%
rmdir /q bin
mkdir bin

echo "@echo off" > %BALC%
echo "PYTHON=%PYTHON%"
echo "PYTHONPATH=%CD%\python" >> %BALC%
echo "%%PYTHON%% %%*" >> %BALC%
