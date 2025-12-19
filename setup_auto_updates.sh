#!/bin/bash
# Setup automated updates on EC2 via cron
# Runs Vegas scraper and predictions every 30 minutes

echo "Setting up cron jobs for automated updates..."

# Create crontab entries
(crontab -l 2>/dev/null; echo "# NFL Auto-Update: Scrape Vegas lines and regenerate predictions every 30 minutes") | crontab -
(crontab -l 2>/dev/null; echo "*/30 * * * * cd /home/ubuntu/H.C.-Lombardo-App && source venv/bin/activate && python scrape_vegas_lines.py >> logs/vegas_scraper.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/30 * * * * cd /home/ubuntu/H.C.-Lombardo-App && source venv/bin/activate && python ml/predict_week.py >> logs/predictions.log 2>&1") | crontab -

echo "✅ Cron jobs installed!"
echo ""
echo "Current crontab:"
crontab -l
