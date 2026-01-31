# 📟 ARCHITECT PUSH PROTOCOL (v1.0)
# Purpose: Syncs only lean logic to GitHub & Vercel.

$commitMsg = $args[0]
if (-not $commitMsg) {
    $commitMsg = "chore: automated sync [Lean Mode]"
}

Write-Host "🚀 Starting Deployment Sync..." -ForegroundColor Cyan

# 1. Verification of Lean Git
Write-Host "📦 Cleaning context killers..." -ForegroundColor Yellow
git add .
git status

# 2. Local Commit
Write-Host "💾 Committing logic..." -ForegroundColor Green
git commit -m $commitMsg

# 3. Remote Sync
Write-Host "🌍 Pushing to GitHub (main)..." -ForegroundColor Blue
git push origin main

# 4. Success Signal
Write-Host "✅ Lean logic synced to: https://github.com/SrAndres629/web-y-tracking-supabase-jorge" -ForegroundColor White
Write-Host "⚡ Vercel Deployment should trigger automatically." -ForegroundColor Magenta
