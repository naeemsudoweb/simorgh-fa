# ================================================================
# One-click setup & run.
# First run: installs packages, creates .env for you (asks for an
#            admin password once), then starts the site.
# Every run after that: just starts the site immediately.
# ================================================================

Write-Host "Installing required packages..." -ForegroundColor Cyan
python -m pip install -r requirements.txt --quiet

if (!(Test-Path ".env")) {
    Write-Host ""
    Write-Host "First time setup: creating your .env file..." -ForegroundColor Cyan

    $secretKey = python -c "import secrets; print(secrets.token_hex(32))"

    $securePassword = Read-Host "Choose an admin panel password" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)

    $env:TEMP_ADMIN_PW = $plainPassword
    $hash = python -c "import os; from werkzeug.security import generate_password_hash; print(generate_password_hash(os.environ['TEMP_ADMIN_PW']))"
    Remove-Item Env:\TEMP_ADMIN_PW

    $envContent = "SECRET_KEY=$secretKey`nADMIN_USERNAME=admin`nADMIN_PASSWORD_HASH=$hash`nFLASK_DEBUG=false`n"
    $envContent | Out-File -FilePath ".env" -Encoding ascii -NoNewline

    Write-Host ""
    Write-Host "Done. Admin username: admin  (password is the one you just typed)" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starting the site... (press Ctrl+C to stop)" -ForegroundColor Cyan
Write-Host "Once it's running, open: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host ""
python app.py
