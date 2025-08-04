import os
import subprocess
import urllib.error
import urllib.request

def get_filename_without_extension(path):
  filename = os.path.basename(path)
  # Handle common compound extensions
  for ext in ['.tar.gz', '.tar.xz', '.tar.bz2']:
    if filename.endswith(ext):
      return filename[:-len(ext)]
  # Fall back to simple extension
  return os.path.splitext(filename)[0]

def url_exists_urllib(s_url: str) -> bool:
  o_request = urllib.request.Request(s_url, method='HEAD')
  try:
    with urllib.request.urlopen(o_request) as o_response:
      if o_response.status != 200:
        return False
  except urllib.error.HTTPError as o_err:
    return False
  except urllib.error.URLError as o_err:
    return False
  return True


#def url_exists_curl(str_url: str) -> bool:
#  try:
#    subprocess.check_call([
#      "curl",
#      "-s",  # silent
#      "-I",  # headers only
#      "--fail",  # fail on 404 or other errors
#      str_url
#    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#    return True
#  except subprocess.CalledProcessError:
#    return False

def is_https_resource_available(str_url: str) -> bool:
  return url_exists_urllib(str_url)

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

def pull_repo(dest_folder, branch):
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

def flatten_if_single_subfolder(str_destination_folder):
  if not os.path.isdir(str_destination_folder):
    return

  entries = os.listdir(str_destination_folder)
  if len(entries) != 1:
    return

  str_inner_path = os.path.join(str_destination_folder, entries[0])
  if not os.path.isdir(str_inner_path):
    return

  str_temp_name = str_destination_folder + "_tmp_"
  os.rename(str_destination_folder, str_temp_name)
  os.rename(os.path.join(str_temp_name, entries[0]), str_destination_folder)
  os.rmdir(str_temp_name)
