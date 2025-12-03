import subprocess

def run_shell_command(command):
    print(f"➡️  Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stdout}")
        return False, result.stderr
    if result.stdout:
        print(f"✅ Output: {result.stdout}")
    return True, result.stdout
