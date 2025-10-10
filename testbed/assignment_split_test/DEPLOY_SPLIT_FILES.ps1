# Deploy Split Assignment Files

Write-Host "`n" -NoNewline
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host " DEPLOY SPLIT ASSIGNMENT FILES - TESTBED VALIDATED " -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

Write-Host "`nTestbed Validation:" -ForegroundColor Yellow
Write-Host "   ✅ README.md created (overview + navigation)" -ForegroundColor Green
Write-Host "   ✅ week1.md created (Sept 2025 assignment)" -ForegroundColor Green
Write-Host "   ✅ weeks2-4.md created (Oct 2025 upgrades)" -ForegroundColor Green

Write-Host "`nProceeding with Production Deployment..." -ForegroundColor Yellow
Write-Host "   Step 1: Git safety commit" -ForegroundColor White

# Step 1: Safety commit
cd "c:\IS330\H.C Lombardo App"
git add -A
git commit -m "Pre-change safety commit - before splitting assignment files"

Write-Host "   ✅ Safety commit created" -ForegroundColor Green
Write-Host "`n   Step 2: Copy files to dr.foster/ folder" -ForegroundColor White

# Step 2: Copy split files to production
Copy-Item "testbed\assignment_split_test\README.md" "dr.foster\README.md" -Force
Copy-Item "testbed\assignment_split_test\week1.md" "dr.foster\week1.md" -Force
Copy-Item "testbed\assignment_split_test\weeks2-4.md" "dr.foster\weeks2-4.md" -Force

Write-Host "   ✅ Copied 3 files to dr.foster/" -ForegroundColor Green
Write-Host "`n   Step 3: Verify files" -ForegroundColor White

# Step 3: Verify
$files = Get-ChildItem "dr.foster\*.md" | Select-Object -ExpandProperty Name
Write-Host "`n   Files in dr.foster/:" -ForegroundColor Cyan
foreach ($file in $files) {
    Write-Host "      ✅ $file" -ForegroundColor Green
}

Write-Host "`n   Step 4: Keep or archive assignment.md?" -ForegroundColor White
if (Test-Path "dr.foster\assignment.md") {
    # Rename old file to archive
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Move-Item "dr.foster\assignment.md" "dr.foster\assignment_archive_$timestamp.md"
    Write-Host "   ✅ Archived old assignment.md → assignment_archive_$timestamp.md" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No old assignment.md to archive" -ForegroundColor Yellow
}

Write-Host "`n   Step 5: Git commit and push" -ForegroundColor White

# Step 5: Commit changes
git add -A
git commit -m "ORGANIZE: Split assignment into week1.md and weeks2-4.md with README overview"
git push origin master

Write-Host "   ✅ Committed and pushed to GitHub" -ForegroundColor Green

Write-Host "`n" -NoNewline
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host " DEPLOYMENT COMPLETE! " -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green

Write-Host "`nWhat Changed:" -ForegroundColor Yellow
Write-Host "   • Created README.md (overview + navigation)" -ForegroundColor Green
Write-Host "   • Created week1.md (Week 1 assignment)" -ForegroundColor Green
Write-Host "   • Created weeks2-4.md (Weeks 2-4 upgrades)" -ForegroundColor Green
Write-Host "   • Archived old assignment.md" -ForegroundColor Cyan

Write-Host "`nDr. Foster Folder Structure:" -ForegroundColor Yellow
Write-Host "   dr.foster/" -ForegroundColor Cyan
Write-Host "      ├─ README.md" -ForegroundColor White -NoNewline
Write-Host " ← START HERE! (overview)" -ForegroundColor Yellow
Write-Host "      ├─ week1.md" -ForegroundColor White -NoNewline
Write-Host " ← Week 1 assignment" -ForegroundColor Gray
Write-Host "      └─ weeks2-4.md" -ForegroundColor White -NoNewline
Write-Host " ← Weeks 2-4 assignment" -ForegroundColor Gray

Write-Host "`nEasy navigation for Dr. Foster! 📚" -ForegroundColor Green
Write-Host ""
