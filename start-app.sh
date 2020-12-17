. ./env/Scripts/activate
reset
echo Starting up app.py...
python app.py
watchmedo shell-command --pattern="*app.py;*.sql" --drop --recursive --command="cls && echo Restarting app due to save event... && python app.py && echo App completed normally || echo App exited with code $?" .