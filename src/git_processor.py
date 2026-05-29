import os
import sys
import stat
import subprocess

def _remove_dir_tree(path):
    """Remove a directory tree recursively."""
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            fp = os.path.join(root, name)
            os.chmod(fp, stat.S_IWRITE)
            os.remove(fp)
        for name in dirs:
            fp = os.path.join(root, name)
            try:
                os.rmdir(fp)
            except OSError:
                os.chmod(fp, stat.S_IWRITE)
                os.remove(fp)
    os.rmdir(path)

def _run_git(cmd, cwd):
    import sys
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    result = subprocess.run(["git"] + cmd, capture_output=True, text=True, cwd=cwd, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    return result.stdout.strip()

def main(target_dir, dates):
    """Generate a git repo with empty commits for the given dates."""
    remote_url = None
    git_path = os.path.join(target_dir, ".git")
    
    if os.path.exists(git_path):
        try:
            remote_url = _run_git(["remote", "get-url", "origin"], target_dir)
        except RuntimeError:
            pass
        _remove_dir_tree(git_path)

    os.makedirs(target_dir, exist_ok=True)
    _run_git(["init", "."], target_dir)

    message = "Commit made by Paint with Git\nhttps://github.com/Fascial/Paint-with-Git\nFor Contact Details visit http://ghazarat.space/\n"
    
    try:
        name = _run_git(["config", "--global", "user.name"], target_dir)
        email = _run_git(["config", "--global", "user.email"], target_dir)
    except Exception:
        name = "Paint with Git User"
        email = "user@example.com"

    import datetime
    stream_lines = []
    message_bytes = message.encode("utf-8")
    
    commit_dates = dates if dates else ["2000-01-01"]
    
    for date in commit_dates:
        dt_obj = datetime.datetime.strptime(date, "%Y-%m-%d").replace(hour=12)
        timestamp = int(dt_obj.timestamp())
        
        stream_lines.append(b"commit refs/heads/main")
        stream_lines.append(f"committer {name} <{email}> {timestamp} +0000".encode("utf-8"))
        stream_lines.append(f"data {len(message_bytes)}".encode("utf-8"))
        stream_lines.append(message_bytes)

    stream_data = b"\n".join(stream_lines) + b"\n"
    
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        
    res = subprocess.run(["git", "fast-import"], input=stream_data, cwd=target_dir, capture_output=True, **kwargs)
    if res.returncode != 0:
        raise RuntimeError(f"fast-import failed:\n{res.stderr.decode('utf-8', errors='replace')}")

    if dates:
        count_msg = f"Created {len(dates)} commits."
    else:
        count_msg = "Created clean slate (1 placeholder commit)."

    _run_git(["branch", "-M", "main"], target_dir)

    if remote_url:
        _run_git(["remote", "add", "origin", remote_url], target_dir)

    return count_msg
