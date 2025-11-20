@echo off
git add .
git commit -m "Update: %date%"
git push origin main
echo  Todo subido a GitHub!
timeout 3
