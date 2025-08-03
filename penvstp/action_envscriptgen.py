from penvstp.model_types import StepContext, HostArch
import os

def handle_env_script(step_ctx: StepContext):
  exec_ctx = step_ctx.configuration()
  step = step_ctx.step()

  if not step.params.env_vars or not step.params.output_name:
    raise ValueError("[GENENVSCRIPT] Missing 'env_vars' or 'output_name' for generate_env_script action")

  lines = []
  for v in step.params.env_vars:
    if not isinstance(v, dict):
      raise ValueError("[GENENVSCRIPT] env_vars must be a dictionary with 'name' and 'reference_id' keys")
    if not "name" in v:
      raise ValueError("[GENENVSCRIPT] env_vars must contain 'name' key")
    if not "reference_id" in v:
      raise ValueError("[GENENVSCRIPT] env_vars must contain 'reference_id' key")

    ref_id = v["reference_id"]
    reference_step = step_ctx.get_step_by_id(ref_id)
    if not reference_step:
      raise RuntimeError(f"[GENENVSCRIPT] Reference step '{ref_id}' not found")
    var_val = reference_step.get_destination_folder()
    if not var_val:
      raise RuntimeError(f"[GENENVSCRIPT] Reference step '{ref_id}' has no destination folder")

    if exec_ctx.host_arch == HostArch.WindowsX64:
      lines.append(f"set {v['name']}={var_val}")
    else:
      lines.append(f"export {v['name']}={var_val}")

  ext = ".sh"
  if exec_ctx.host_arch == HostArch.WindowsX64:
    ext = ".bat"

  output_path = step.params.output_name + ext
  if exec_ctx.is_want_dst():
    destination_exists = False
    if exec_ctx.is_dry():
      if exec_ctx.is_dry_dest():
        print(f"[GENENVSCRIPT] Assuming output path {output_path} exists")
        destination_exists = True
      else:
        print(f"[GENENVSCRIPT] Assuming output path {output_path} does not exist")
        destination_exists = False
    else:
      destination_exists = os.path.exists(output_path)

    if destination_exists:
      print(f"[GENENVSCRIPT] Output file {output_path} already exists")
    else:
      if exec_ctx.is_check_only():
        raise RuntimeError(f"[GENENVSCRIPT] Output file {output_path} does not exist")

    create_script = exec_ctx.is_force() or not destination_exists
    if create_script:
      if exec_ctx.is_dry():
        print(f"[GENENVSCRIPT] Would create environment script at {output_path} with lines: {lines}")
      else:
        print(f"[GENENVSCRIPT] Creating environment script at {output_path} with lines: {lines}")
        with open(output_path, 'w') as f:
          f.write('\n'.join(lines))

  print(f"[GENENVSCRIPT] Finished")
