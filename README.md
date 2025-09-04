# ProjectTimeManager – Deployment Guide

This document provides step-by-step instructions to install, configure, and run the **TaskManager** Django application using `uv`, `gunicorn`, and `systemd`.

---

## 1. Install Dependencies

Install **uv** (a fast Python package manager):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install required Python packages:

```bash
uv pip install -r TaskManager/requirements.txt
```

---

## 2. Run Gunicorn Manually (Test Mode)

Navigate to the project folder and start `gunicorn`:

```bash
cd ProjectTimeManager/TaskManager
../.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 TaskManager.wsgi:application
```

- **workers 3** → Handles multiple requests concurrently.  
- **bind 0.0.0.0:8000** → Accessible on port `8000` from all interfaces.  
- **TaskManager.wsgi:application** → Entry point for the Django app.  

---

## 3. Setup Gunicorn as a Systemd Service

Create a service file:

```bash
sudo nano /etc/systemd/system/tasktimer.service
```

Add the following:

```ini
[Unit]
Description=gunicorn daemon for Django project
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ProjectTimeManager/TaskManager
ExecStart=/home/ubuntu/ProjectTimeManager/.venv/bin/gunicorn   --workers 3   --bind 0.0.0.0:8000   TaskManager.wsgi:application

[Install]
WantedBy=multi-user.target
```

---

## 4. Enable & Manage the Service

Reload `systemd` to recognize the new service:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
```

Enable service to start on boot:

```bash
sudo systemctl enable tasktimer
```

Start the service:

```bash
sudo systemctl start tasktimer
```

Check service status:

```bash
sudo systemctl status tasktimer
```

Restart if needed:

```bash
sudo systemctl restart tasktimer
```

---

## 5. Logs & Debugging

View real-time logs:

```bash
journalctl -u tasktimer -f
```

---

✅ At this point, the Django application should be running on **port 8000** via `gunicorn`, managed by `systemd`.  
