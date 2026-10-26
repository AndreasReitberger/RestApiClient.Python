rem dir C:\Users\q36606\.pypirc
rem type C:\Users\q36606\.pypirc
rem python -m twine upload --repository gitea --verbose dist/*
rem python -c "import configparser; c=configparser.ConfigParser(); c.read(r'C:\Users\q36606\.pypirc'); print(c.sections())"
rem pause
rem pip config -v list
python -m twine upload --config-file "C:\Users\q36606\.pypirc" --repository gitea dist/*
pause