tmux -S shared kill-session -t am4shared
tmux -S shared new -s am4shared python3 acdbbot.py
