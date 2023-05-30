tmux -S shared kill-session -t monitor
tmux -S shared new -s monitor python3 monitor.py
