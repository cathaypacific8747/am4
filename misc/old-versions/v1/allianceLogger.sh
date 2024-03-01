tmux -S shared kill-session -t allianceLog
tmux -S shared new -s allianceLog python3 allianceLogger.py
