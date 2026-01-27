@echo off
echo ========================================
echo Rebuild and Test xtquant Import
echo ========================================
echo.

echo [1/4] Cleaning old build files...
if exist build_simple_test rmdir /s /q build_simple_test >nul 2>&1
if exist build_xtquant_test rmdir /s /q build_xtquant_test >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1
echo [OK] Cleaned

echo.
echo [2/4] Building simple import test...
pyinstaller simple_import_test.spec
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo [OK] Build completed

echo.
echo [3/4] Checking QMT port status...
netstat -ano | findstr :58610 >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Port 58610 is listening - QMT appears to be running
) else (
    echo [WARNING] Port 58610 not found - QMT may not be running
)

echo.
echo [4/4] Running built application...
cd build_simple_test
echo Starting simple_import_test.exe...
simple_import_test.exe

echo.
echo ========================================
echo Test completed!
echo If you see "SUCCESS: xtdata imported", the packaging works!
echo If you see import errors, check the spec file hiddenimports.
echo ========================================
pause
