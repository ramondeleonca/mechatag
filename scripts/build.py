import os
import subprocess as sp
import zipfile
import sys
from PyInstaller import __main__ as pyinstaller

if __name__ == "__main__":
    if not "--onlyzip" in sys.argv:
        # Build frontend first
        sp.run(args="npm run build", shell=True, cwd="src/frontend")

        # Build distributable
        pyinstaller.run([
            '--paths src',
            '--name=mechatag',
            f'--add-data=src/frontend/dist{os.pathsep}frontend/dist',
            '-y',
            # 'main.py',

            '--hidden-import camera_adapters.uvc_camera_adapter',
            '--hidden-import camera_adapters.pi_camera_adapter',

            '--hidden-import output_adapters.console_output_adapter',
            '--hidden-import output_adapters.pi_uart_output_adapter'
        ])

    # Zip the dist folder
    print("Zipping the dist folder...")
    dist_dir = "dist"
    zipf = zipfile.ZipFile('mechatag.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            zipf.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(dist_dir, '..')))