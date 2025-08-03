from penvstp.model_types import StepContext
from penvstp.helpers import is_https_resource_available, is_local_git_repo, local_and_remote_repo_version_match, pull_repo, clone_repo

def handle_pull(step_ctx: StepContext):
  exec_ctx = step_ctx.configuration()
  step = step_ctx.step()
  if not step.params.url:
    raise ValueError("[PULL] Missing 'url' parameter")
  repo_url = step.params.url

  repo_reachable = False

  if exec_ctx.is_dry():
    if exec_ctx.is_dry_src():
      print(f"[PULL] Assuming {repo_url} exits")
      repo_reachable = True
    else:
      print(f"[PULL] Assuming {repo_url} unreachable")
      repo_reachable = False
  else:
    print(f"[PULL] Verifying repository: {repo_url}")
    repo_reachable = is_https_resource_available(repo_url)

  if not repo_reachable:
    raise RuntimeError(f"[PULL] Repository not reachable: {repo_url}")

  dest_path = step_ctx.get_destination_folder()
  if not dest_path:
    raise ValueError("[PULL] Can't determine local destination path")

  if exec_ctx.is_want_dst():
    destination_exists = False
    if exec_ctx.is_dry():
      if exec_ctx.is_dry_dest():
        print(f"[PULL] Assuming {dest_path} exists")
        destination_exists = True
      else:
        print(f"[PULL] Assuming {dest_path} doesn't exists")
        destination_exists = False
    else:
      destination_exists = is_local_git_repo(dest_path)
      print(f"[PULL] Clone destination: {dest_path} ({'already exists' if destination_exists else 'does not exist'})")

    if destination_exists:
      dest_uptodate = False
      if exec_ctx.is_dry():
        if exec_ctx.is_dry_stale():
          print(f"[PULL] Assuming {dest_path} is not at latest version")
          dest_uptodate = False
        else:
          print(f"[PULL] Assuming {dest_path} is at latest version")
          dest_uptodate = True
      else:
        print(f"[PULL] Comparing local and remote version")
        dest_uptodate = local_and_remote_repo_version_match(repo_url, dest_path)

      if not dest_uptodate:
        if exec_ctx.is_check_only():
          raise RuntimeError(f"[PULL] Repository not at the latest version")

      do_update = exec_ctx.is_force() or not dest_uptodate
      if do_update:
        if exec_ctx.is_dry():
          print(f"[PULL] Would pull {repo_url} to {dest_path}")
        else:
          print(f"[PULL] Performing git pull {repo_url} to {dest_path}")
          pull_repo(dest_path, None)
      else:
        print(f"[PULL] Local version up to date")
    else:
      if exec_ctx.is_check_only():
        raise RuntimeError(f"[PULL] Local repository doesn't exist")
      if exec_ctx.is_dry():
        print(f"[PULL] Would clone {repo_url} to {dest_path}")
      else:
        print(f"[PULL] Performing git clone {repo_url} to {dest_path}")
        clone_repo(repo_url, dest_path, None)

  print(f"[PULL] Finished")
