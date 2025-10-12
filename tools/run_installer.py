import subprocess
import os

print("Running HDRI Light Studio installer...")
os.chdir(r"e:\Projects\HDRI_editor\tools")
result = subprocess.run(["python", "build_and_install_hdri_light_studio.py"], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")  
print(result.stderr)
print(f"\nReturn code: {result.returncode}")