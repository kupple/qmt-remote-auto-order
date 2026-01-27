@echo off
echo ========================================
echo Build Simple xtquant Import Test
echo ========================================
echo.

echo Step 1: Check PyInstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller not found
    echo Please install: pip install pyinstaller
    pause
    exit /b 1
)
echo [OK] PyInstaller found

echo.
echo Step 2: Clean old build
if exist build_simple_test rmdir /s /q build_simple_test
if exist dist rmdir /s /q dist
echo [OK] Cleaned

echo.
echo Step 3: Build with PyInstaller
pyinstaller simple_import_test.spec
if %errorlevel% neq 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)
echo [OK] Build completed

echo.
echo Step 4: Test the built executable
cd build_simple_test
echo Running built executable...
simple_import_test.exe
cd ..

echo.
echo ========================================
echo Build and test completed!
echo If import succeeds, xtquant packaging works
echo If import fails, check the spec file configuration
echo ========================================
pause
