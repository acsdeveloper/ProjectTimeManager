UV Installation:
curl -LsSf https://astral.sh/uv/install.sh | sh

uv pip install -r TaskManager/requirements.txt


cd ProjectTimeManager/TaskManager
ProjectTimeManager/.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 TaskManager.wsgi:application


sudo nano /etc/systemd/system/tasktimer.service


[Unit]
Description=gunicorn daemon for Django project
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ProjectTimeManager/TaskManager
ExecStart=/home/ubuntu/ProjectTimeManager/.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 TaskManager.wsgi:application

[Install]
WantedBy=multi-user.target