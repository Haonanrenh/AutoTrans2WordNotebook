$ErrorActionPreference = "Stop"

$DictionaryPath = "src/resources/builtin_dictionary.sqlite3"
if (-not (Test-Path $DictionaryPath)) {
    throw "Missing $DictionaryPath. Run: python tools/build_ecdict.py"
}

python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    throw "pip install failed with exit code $LASTEXITCODE"
}

pyinstaller packaging/wordtrans_notebook.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host "Build finished: dist/自动选词记录单词本.exe"
