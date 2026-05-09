rd /s /q build
rd /s /q dist
pyinstaller --clean --onefile --windowed --paths src --add-data "locale;locale" --icon=assets/icon.ico --name U-Prox-USB src/main.py