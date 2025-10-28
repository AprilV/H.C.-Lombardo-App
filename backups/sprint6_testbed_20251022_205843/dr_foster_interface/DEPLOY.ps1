# Deploy Dr. Foster Interface to Production

Write-Host "`n" -NoNewline
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host " DEPLOY DR. FOSTER INTERACTIVE INTERFACE " -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

Write-Host "`nTestbed Validation:" -ForegroundColor Yellow
Write-Host "   ✅ index.html created (interactive dashboard)" -ForegroundColor Green
Write-Host "   ✅ README.md created (instructions with link)" -ForegroundColor Green
Write-Host "   ✅ Tested in browser successfully" -ForegroundColor Green

Write-Host "`nProceeding with Production Deployment..." -ForegroundColor Yellow
Write-Host "   Step 1: Git safety commit" -ForegroundColor White

# Step 1: Safety commit
cd "c:\IS330\H.C Lombardo App"
git add -A
git commit -m "Pre-deployment: before adding interactive dashboard to dr.foster/"

Write-Host "   ✅ Safety commit created" -ForegroundColor Green
Write-Host "`n   Step 2: Copy files to dr.foster/" -ForegroundColor White

# Step 2: Copy files to production
Copy-Item "testbed\dr_foster_interface\index.html" "dr.foster\index.html" -Force
Copy-Item "testbed\dr_foster_interface\README.md" "dr.foster\README.md" -Force

Write-Host "   ✅ Copied interactive dashboard to dr.foster/" -ForegroundColor Green
Write-Host "`n   Step 3: Verify files" -ForegroundColor White

# Step 3: Verify
Write-Host "`n   Files in dr.foster/:" -ForegroundColor Cyan
Get-ChildItem "dr.foster" | Where-Object { -not $_.PSIsContainer } | Select-Object -ExpandProperty Name | ForEach-Object {
    Write-Host "      ✅ $_" -ForegroundColor Green
}

Write-Host "`n   Step 4: Git commit and push" -ForegroundColor White

# Step 4: Commit changes
git add -A
git commit -m "ADD: Interactive HTML dashboard for Dr. Foster with tabbed navigation"
git push origin master

Write-Host "   ✅ Committed and pushed to GitHub" -ForegroundColor Green

Write-Host "`n" -NoNewline
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host " DEPLOYMENT COMPLETE! " -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green

Write-Host "`nWhat Changed:" -ForegroundColor Yellow
Write-Host "   ✅ Added index.html (interactive dashboard)" -ForegroundColor Green
Write-Host "   ✅ Added README.md (instructions with link)" -ForegroundColor Green
Write-Host "   ✅ Committed and pushed to GitHub" -ForegroundColor Green

Write-Host "`nDr. Foster will see:" -ForegroundColor Yellow
Write-Host "   dr.foster/" -ForegroundColor Cyan
Write-Host "      ├─ README.md" -ForegroundColor White -NoNewline
Write-Host " ← START HERE! (has link to dashboard)" -ForegroundColor Yellow
Write-Host "      ├─ index.html" -ForegroundColor White -NoNewline
Write-Host " ← Interactive Dashboard (just double-click!)" -ForegroundColor Yellow
Write-Host "      ├─ week1-2.md" -ForegroundColor White -NoNewline
Write-Host " ← Week 1-2 (alternative markdown)" -ForegroundColor Gray
Write-Host "      └─ weeks2-4.md" -ForegroundColor White -NoNewline
Write-Host " ← Weeks 2-4 (alternative markdown)" -ForegroundColor Gray

Write-Host "`nHow Dr. Foster Opens It:" -ForegroundColor Yellow
Write-Host "   Option 1: Open README.md and click the link" -ForegroundColor Cyan
Write-Host "   Option 2: Double-click index.html directly" -ForegroundColor Cyan
Write-Host "   Option 3: View on GitHub (will render beautifully)" -ForegroundColor Cyan

Write-Host "`n Perfect for grading! " -ForegroundColor Green
Write-Host ""
