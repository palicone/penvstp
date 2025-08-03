from penvstp.model_types import StepContext
import subprocess

def handle_gitcmd(step_ctx: StepContext):
  exec_ctx = step_ctx.configuration()
  step = step_ctx.step()
  if not step.params.reference_id:
    raise ValueError("[GITCMD] Missing 'reference_id'")
  if not step.params.cmd:
    raise ValueError("[GITCMD] Missing 'cmd'")
  ref_step_ctx = step_ctx.get_ref_step()
  if not ref_step_ctx:
    raise ValueError(f"[GITCMD] No referenced step for step index {step_ctx.index()}")

  source_path = ref_step_ctx.get_destination_folder()
  if not source_path:
    raise ValueError(f"[GITCMD] Referenced step destination path undetermined")

  if exec_ctx.is_want_dst():
    full_cmd = ["git", "-C", source_path] + step.params.cmd.split()
    if exec_ctx.is_dry():
      print(f"[GITCMD] Would execute: {' '.join(full_cmd)}")
    else:
      print(f"[GITCMD] Running: {' '.join(full_cmd)}")
      subprocess.check_call(full_cmd)

  print(f"[GITCMD] Finished")
