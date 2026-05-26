import argparse
import os
import shlex
import subprocess
import sys
import time

# Configuration
GIT_REMOTE = "origin"
GIT_BRANCH = "main"

# Remote deployment settings.
# Update these values before using the script.
REMOTE_HOST = "ec2-user@your-ec2-host.amazonaws.com"
SSH_KEY = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_PATH = "~/cloudrun"
PYTHON_CMD = "python3"

WATCHED_EXTENSIONS = {"py", "html", "css", "js", "md", "txt"}
WATCH_IGNORE_DIRS = {".git", "__pycache__"}


def run_local(command, cwd=None, capture_output=False, check=True):
    result = subprocess.run(
        shlex.split(command) if isinstance(command, str) else command,
        cwd=cwd,
        capture_output=capture_output,
        text=True,
        check=check,
    )
    return result.stdout.strip() if capture_output else None


def has_git_changes():
    status = run_local(["git", "status", "--short"], capture_output=True)
    return bool(status.strip())


def get_repo_url():
    return run_local(["git", "config", "--get", f"remote.{GIT_REMOTE}.url"], capture_output=True)


def git_add_commit_push(message=None):
    if not has_git_changes():
        print("No local changes detected.")
        return False

    run_local(["git", "add", "."])
    message = message or f"Auto deploy commit {time.strftime('%Y-%m-%d %H:%M:%S')}"
    run_local(["git", "commit", "-m", message])
    print("Committed local changes.")
    run_local(["git", "push", GIT_REMOTE, GIT_BRANCH])
    print("Pushed changes to Git remote.")
    return True


def ssh_command(command):
    ssh_base = ["ssh", "-i", SSH_KEY, REMOTE_HOST]
    return run_local(ssh_base + [command], capture_output=True)


def remote_command(command):
    if isinstance(command, list):
        command = " ".join(shlex.quote(str(part)) for part in command)
    return ssh_command(command)


def ensure_remote_repo():
    repo_url = get_repo_url()
    if not repo_url:
        raise RuntimeError("Could not read remote repo URL from git config.")

    print(f"Ensuring remote repo exists at {REMOTE_PATH}")
    check_dir = f"if [ -d {REMOTE_PATH}/.git ]; then echo exists; fi"
    exists = remote_command(check_dir)
    if "exists" in exists:
        print("Remote repo already cloned. Pulling latest changes...")
        remote_command(f"cd {REMOTE_PATH} && git pull {GIT_REMOTE} {GIT_BRANCH}")
    else:
        print("Remote repo not found. Cloning...")
        remote_command(f"mkdir -p {REMOTE_PATH} && cd {os.path.dirname(REMOTE_PATH)} && git clone {repo_url} {os.path.basename(REMOTE_PATH)}")


def start_remote_apps():
    print("Starting remote Flask apps...")
    commands = [
        f"cd {REMOTE_PATH} && pkill -f 'python3 logic/app.py' || true",
        f"cd {REMOTE_PATH} && pkill -f 'python3 rectangle_app/app.py' || true",
        f"cd {REMOTE_PATH} && nohup {PYTHON_CMD} logic/app.py > logic.log 2>&1 &",
        f"cd {REMOTE_PATH} && nohup {PYTHON_CMD} rectangle_app/app.py > rectangle_app.log 2>&1 &",
    ]
    for cmd in commands:
        remote_command(cmd)
    print("Remote apps started.")


def deploy_now(message=None):
    changes = git_add_commit_push(message=message)
    if not changes:
        print("Skipping remote deployment because there are no changes.")
        return
    ensure_remote_repo()
    start_remote_apps()
    print("Deployment complete.")


def watch_loop(interval=2):
    try:
        import watchdog.events
        import watchdog.observers
    except ImportError:
        print("watchdog is not installed. Install it with: pip install watchdog")
        sys.exit(1)

    class ChangeHandler(watchdog.events.FileSystemEventHandler):
        def on_any_event(self, event):
            if event.is_directory:
                return
            if any(ignore in event.src_path for ignore in WATCH_IGNORE_DIRS):
                return
            if os.path.splitext(event.src_path)[1].lstrip(".") not in WATCHED_EXTENSIONS:
                return
            print(f"Detected change: {event.src_path}")
            deploy_now()

    observer = watchdog.observers.Observer()
    handler = ChangeHandler()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()
    print("Watching for file changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(interval)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def parse_args():
    parser = argparse.ArgumentParser(description="Auto push and remote deploy helper")
    parser.add_argument("--deploy", action="store_true", help="Commit/push changes and deploy to remote immediately")
    parser.add_argument("--watch", action="store_true", help="Watch local files and deploy automatically on change")
    parser.add_argument("--message", type=str, help="Commit message for auto deploy")
    parser.add_argument("--remote-host", type=str, help="Override the SSH remote host/user")
    parser.add_argument("--ssh-key", type=str, help="Override the SSH private key path")
    parser.add_argument("--remote-path", type=str, help="Override the remote project path")
    parser.add_argument("--python-cmd", type=str, help="Override the remote Python command")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.remote_host:
        global REMOTE_HOST
        REMOTE_HOST = args.remote_host
    if args.ssh_key:
        global SSH_KEY
        SSH_KEY = os.path.expanduser(args.ssh_key)
    if args.remote_path:
        global REMOTE_PATH
        REMOTE_PATH = args.remote_path
    if args.python_cmd:
        global PYTHON_CMD
        PYTHON_CMD = args.python_cmd

    if args.watch:
        watch_loop()
    elif args.deploy:
        deploy_now(message=args.message)
    else:
        print("Nothing to do. Use --deploy to push and deploy, or --watch to auto deploy on file changes.")


if __name__ == "__main__":
    main()
