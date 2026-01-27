#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Standalone xtquant test runner
No batch files needed, pure Python
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description=""):
    """Run a command and return (success, output)"""
    print("
{}Running: {}".format(description, ' '.join(cmd) if isinstance(cmd, list) else cmd))

    try:
        if isinstance(cmd, list):
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

        success = result.returncode == 0
        output = result.stdout + result.stderr

        if success:
            print("[OK] Command completed successfully")
        else:
            print("[ERROR] Command failed with code {}".format(result.returncode))

        if output.strip():
            print("Output:")
            print(output)

        return success, output

    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out")
        return False, ""
    except Exception as e:
        print("[ERROR] Exception: {}".format(e))
        return False, ""

def check_qmt_port():
    """Check if QMT port 58610 is listening"""
    print("\n" + "="*50)
    print("Checking QMT port status...")

    success, output = run_command("netstat -ano", "Port check")

    if success and ":58610" in output:
        print("[SUCCESS] Port 58610 is listening - QMT appears to be running")
        return True
    else:
        print("[WARNING] Port 58610 not found in listening state")
        print("Please make sure QMT Professional or QMT Lite is running")
        return False

def run_xtquant_test():
    """Run the main xtquant test"""
    print("\n" + "="*50)
    print("Running xtquant connection test...")

    # Check if test file exists
    test_file = "test_xtquant_connection.py"
    if not os.path.exists(test_file):
        print("[ERROR] Test file '{}' not found".format(test_file))
        return False

    success, output = run_command([sys.executable, test_file], "Test execution")

    return success

def main():
    print("xtquant Standalone Test Runner")
    print("Python version: {}".format(sys.version.split()[0]))
    print("Current directory: {}".format(os.getcwd()))
    print("="*60)

    # Check Python environment
    print("Python executable: {}".format(sys.executable))
    print("Python path: {}".format(sys.path[:3]))  # Show first 3 paths

    # Check QMT port
    qmt_running = check_qmt_port()

    # Run test
    test_success = run_xtquant_test()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print("  QMT Port Check: {}".format("PASS" if qmt_running else "FAIL"))
    print("  Test Execution: {}".format("PASS" if test_success else "FAIL"))

    if qmt_running and test_success:
        print("\n[SUCCESS] All tests passed!")
    elif qmt_running and not test_success:
        print("\n[ISSUE] QMT is running but test failed - possible xtquant library issue")
    else:
        print("\n[ISSUE] QMT may not be running - please start QMT first")

    print("\nPlease send this output to the developer for diagnosis.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
