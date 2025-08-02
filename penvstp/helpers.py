import os
import subprocess

def get_filename_without_extension(path):
  filename = os.path.basename(path)
  # Handle common compound extensions
  for ext in ['.tar.gz', '.tar.xz', '.tar.bz2']:
    if filename.endswith(ext):
      return filename[:-len(ext)]
  # Fall back to simple extension
  return os.path.splitext(filename)[0]

def is_https_resource_available(str_url: str) -> bool:
  try:
    subprocess.check_call([
      "curl",
      "-s",  # silent
      "-I",  # headers only
      "--fail",  # fail on 404 or other errors
      str_url
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True
  except subprocess.CalledProcessError:
    return False

def is_local_git_repo(dest_folder) -> bool:
  if not os.path.exists(dest_folder):
    return False
  return True

def clone_repo(repo_url, dest_folder, branch):
  clone_cmd = ["git", "clone"]
  if branch:
    clone_cmd += ["--branch", branch]
  clone_cmd += [repo_url, dest_folder]
  subprocess.check_call(clone_cmd)

def pull_repo(repo_url, dest_folder, branch):
  pull_cmd = ["git", "-C", dest_folder, "pull"]
  if branch:
    pull_cmd += [branch]
  subprocess.check_call(pull_cmd)

def local_and_remote_repo_version_match(repo_url, dest_folder) -> bool:
  local_commit = subprocess.check_output(
    ["git", "-C", dest_folder, "rev-parse", "HEAD"], text=True
  ).strip()

  remote_commit = subprocess.check_output(
    ["git", "ls-remote", repo_url, "HEAD"], text=True
  ).split()[0]
  if local_commit == remote_commit:
    return True
  return False

