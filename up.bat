git add .
git commit -m "%*"
git push
ssh kaser2206@34.91.66.249 "cd projects/videoflix_backend && git pull && ./env/bin/pip install -r requirements.txt"