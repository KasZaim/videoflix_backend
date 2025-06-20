git add .
git commit -m "%*"
git push
ssh kaser2206@34.91.66.249 "cd projects/videoflix && sudo git pull & sudo .7env/bin/pip install -r requirements.txt"