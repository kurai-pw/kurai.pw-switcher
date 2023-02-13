**Build .exe command** -
```commandline
pyinstaller -F -i 'assets/kurai.png' --windowed --onefile --add-data "assets/folder.png;assets" --clean kurai!switcher.spec
```