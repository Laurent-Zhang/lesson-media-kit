$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Program,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Program $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}

Invoke-Checked python -m ruff format --check .
Invoke-Checked python -m ruff check .
Invoke-Checked python -m mypy src
Invoke-Checked python -m unittest discover -s tests -v
Invoke-Checked python -m build
Invoke-Checked python -m pip_audit

$secretPattern = '(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)'
$safeRepository = (Resolve-Path '.').Path.Replace('\', '/')
git -c "safe.directory=$safeRepository" grep -n -I -E $secretPattern
if ($LASTEXITCODE -eq 0) {
    throw 'Potential secret pattern found in tracked files.'
}
if ($LASTEXITCODE -ne 1) {
    throw "Secret scan failed with exit code $LASTEXITCODE."
}
