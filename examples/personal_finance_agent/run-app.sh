#!/bin/bash
cd /home/runner/workspace/examples/personal_finance_agent
python finance_api.py &
cd frontend
exec npm run dev
