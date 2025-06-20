git add .
git commit -m "%*"
git push
ssh kaser@34.91.66.249 "cd projects/videoflix && sudo git pull & sudo .env/bin/pip install -r requirements.txt"