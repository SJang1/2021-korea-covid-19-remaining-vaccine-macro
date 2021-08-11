# How to build standalone one-file executable

## Windows
### Pyinstaller
```pwsh
> python -m pip install -r requirements.txt -r requirements-dev.txt
> pyinstaller --add-data "kakao/sound/*.mp3;./sound" --onefile vaccine-run-kakao.py
```

### Nuitka
```pwsh
> python -m pip install nuitka zstandard -r requirements.txt
> nuitka --assume-yes-for-downloads --show-scons --no-progress --include-data-file="./kakao/sound/*.mp3=./kakao/sound/" --onefile -o vaccine-run-kakao.exe vaccine-run-kakao.py
```

## macOS
```sh
$ python -m pip install -r requirements.txt -r requirements-mac.txt -r requirements-dev.txt
$ pyinstaller --add-data "kakao/sound/*.mp3:./sound" --onefile vaccine-run-kakao.py
$ chmod +x dist/vaccine-run-kakao
```
