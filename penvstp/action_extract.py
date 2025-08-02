from penvstp.model_types import StepContext
import os
import zipfile
import tarfile

def handle_extract(step_ctx: StepContext):
  exec_ctx = step_ctx.configuration()
  step = step_ctx.step()

  if not step.params.reference_id:
    raise ValueError("[EXTRACT] Missing 'reference_id' for extract action")

  referenced_step = step_ctx.get_ref_step()
  if not referenced_step:
    raise RuntimeError(f"[EXTRACT] Can't determine referenced step")

  source_path = referenced_step.get_destination_file()
  if not source_path:
    raise ValueError(f"[EXTRACT] No path from the referenced step '{step.params.reference_id}'")

  destination_folder = step_ctx.get_destination_folder()

  print(f"[EXTRACT] From {source_path}")
  print(f"[EXTRACT] To {destination_folder}")

  source_exists = False
  if exec_ctx.is_dry():
    if exec_ctx.is_dry_src():
      print(f"[EXTRACT] Assuming source {source_path} exists")
      source_exists = True
    else:
      print(f"[EXTRACT] Assuming source {source_path} does not exist")
      source_exists = False
  else:
    source_exists = os.path.exists(source_path)

  destination_exists = False
  if exec_ctx.is_dry():
    if exec_ctx.is_dry_dest():
      print(f"[EXTRACT] Assuming destination {destination_folder} exists")
      destination_exists = True
    else:
      print(f"[EXTRACT] Assuming destination {destination_folder} does not exist")
      destination_exists = False
  else:
    destination_exists = os.path.exists(destination_folder)

  if destination_exists:
    print(f"[EXTRACT] {destination_folder} already exists")
  else:
    if exec_ctx.is_check_only():
      raise RuntimeError(f"[DOWNLOAD] {destination_folder} does not exist")

  needs_run = exec_ctx.is_force() or not destination_exists
  if needs_run:
    if not source_exists:
      raise RuntimeError(f"[EXTRACT] Source file does not exist: {source_path}")
    if exec_ctx.is_dry():
      print(f"[EXTRACT] Would extract {source_path} to {destination_folder}")
    else:
      print(f"[EXTRACT] Extracting {source_path} to {destination_folder}")
      if source_path.endswith(".zip"):
        with zipfile.ZipFile(source_path, 'r') as zip_ref:
          zip_ref.extractall(destination_folder)
      elif source_path.endswith(".tar.xz"):
        with tarfile.open(source_path, 'r:xz') as tar_ref:
          tar_ref.extractall(destination_folder)

  print(f"[EXTRACT] Finished")
