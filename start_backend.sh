#!/bin/bash
cd /workspaces/abdou.github.io
source osint_env/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
