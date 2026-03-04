#!/bin/bash
cd /home/nico/projects/cleaning_service_fastapi
sudo PYTHONPATH=/home/nico/.local/lib/python3.12/site-packages:/home/nico/projects/SmartClean /usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 80
