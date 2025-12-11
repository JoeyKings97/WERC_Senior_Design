$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "GitHub Upload Script for Cooling Tower Control Stack" -ForegroundColor Cyan
Write-Host "======================================================`n"

# Check if git is installed
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed. Please install Git from https://git-scm.com"
    exit 1
}

# Check if git repo exists
$gitDir = Join-Path $repoRoot ".git"
if (!(Test-Path $gitDir)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Green
    Push-Location $repoRoot
    git init
    git config user.name "Your Name"
    git config user.email "your.email@example.com"
    Pop-Location
}

# Get repository URL from user
$repoUrl = Read-Host "`nEnter your GitHub repository URL (e.g., https://github.com/username/repo.git)"

if (!$repoUrl) {
    Write-Error "Repository URL cannot be empty"
    exit 1
}

# Check if remote already exists
Push-Location $repoRoot
$remoteExists = git remote | Select-String -Pattern "origin"

if ($remoteExists) {
    Write-Host "Updating remote origin..." -ForegroundColor Green
    git remote set-url origin $repoUrl
}
else {
    Write-Host "Adding remote origin..." -ForegroundColor Green
    git remote add origin $repoUrl
}

# Add all files
Write-Host "`nStaging files..." -ForegroundColor Green
git add -A

# Show what will be committed
Write-Host "`nFiles to commit:" -ForegroundColor Cyan
git status

# Commit
Write-Host "`nEnter commit message (default: 'Initial commit - cooling tower control stack'):" -ForegroundColor Yellow
$commitMsg = Read-Host
if (!$commitMsg) {
    $commitMsg = "Initial commit - cooling tower control stack"
}

Write-Host "Committing..." -ForegroundColor Green
git commit -m $commitMsg

# Push
Write-Host "`nPushing to GitHub..." -ForegroundColor Green
git branch -M main
git push -u origin main

Write-Host "`n✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "Repository: $repoUrl" -ForegroundColor Cyan

Pop-Location
