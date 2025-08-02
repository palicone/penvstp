from penvstp.model_types import StepContext
from penvstp.helpers import is_https_resource_available
import os
import urllib.request


class DownloadDotProgress:
  def __init__(self):
    self.n_last_percent = 0

  def __call__(self, n_blocks, n_block_size, n_total_size):
    n_downloaded = n_blocks * n_block_size
    n_percent = min(100, n_downloaded * 100 // n_total_size) if n_total_size else 0

    if n_percent - self.n_last_percent > 1:
      self.n_last_percent = n_percent
      print(".", end='', flush=True)

def handle_download(step_ctx: StepContext):
  exec_ctx = step_ctx.configuration()
  step = step_ctx.step()
  if not step.params.url:
    raise ValueError("[DOWNLOAD] Missing 'url' parameter for download action")
  url = step.params.url

  dest_path = step_ctx.get_destination_file()
  if not dest_path:
    raise ValueError("[DOWNLOAD]  Can't determine local destination path")
  print(f"[DOWNLOAD] From {url}")
  print(f"[DOWNLOAD] To {dest_path}")

  web_resource_exists = False
  if exec_ctx.is_dry():
    if exec_ctx.is_dry_src():
      print(f"[DOWNLOAD] Assuming {url} exits")
      web_resource_exists = True
    else:
      print(f"[DOWNLOAD] Assuming {url} doesn't exits")
      web_resource_exists = False
  else:
    print(f"[DOWNLOAD] Verifying link: {url}")
    web_resource_exists = is_https_resource_available(url)

  if not web_resource_exists:
    raise RuntimeError(f"[DOWNLOAD] Not reachable: {url}")

  destination_exists = False

  if exec_ctx.is_dry():
    if exec_ctx.is_dry_dest():
      print(f"[DOWNLOAD] Assuming {dest_path} exists")
      destination_exists = True
    else:
      print(f"[DOWNLOAD] Assuming {dest_path} doesn't exists")
      destination_exists = False
  else:
    destination_exists = os.path.exists(dest_path)

  if destination_exists:
    print(f"[DOWNLOAD] File {dest_path} already exists")
  else:
    if exec_ctx.is_check_only():
      raise RuntimeError(f"[DOWNLOAD] File {dest_path} does not exist")

  must_download = exec_ctx.is_force() or not destination_exists
  if must_download:
    if exec_ctx.is_dry():
      print(f"[DOWNLOAD] Would download {url} to {dest_path}")
    else:
      print(f"[DOWNLOAD] Downloading ", end='', flush=True)
      os.makedirs(os.path.dirname(dest_path), exist_ok=True)
      urllib.request.urlretrieve(url, dest_path, reporthook=DownloadDotProgress())
      print(f" done")
  print(f"[DOWNLOAD] Finished")
