from penvstp.model_types import *
from penvstp.action_pull import handle_pull
from penvstp.action_download import handle_download
from penvstp.action_extract import handle_extract
from penvstp.action_envscriptgen import handle_env_script
from penvstp.action_gitcmd import handle_gitcmd
from penvstp.model_types import HostArch
import os
import platform
from pathlib import Path

def detect_host_arch():
  system = platform.system()
  machine = platform.machine()
  if system == "Windows" and machine.endswith("64"):
    return HostArch.WindowsX64
  elif system == "Linux":
    if machine in ["x86_64"]:
      return HostArch.LinuxX64
    elif machine in ["aarch64"]:
      return HostArch.LinuxAArch64
  raise RuntimeError(f"Unsupported system/machine combination: {system}/{machine}")

def process_steps(context: ExecutionContext):
  print(f"Running in: {os.getcwd()}")
  print(f"host_arch: {context.host_arch}")
  print(f"temp_folder: {context.temp_folder}")
  print(f"tools_folder: {context.tools_folder}")
  print(f"externals_folder: {context.externals_folder}")
  print(f"run_type: {context.run_type}")
  print(f"run_mode: {context.run_mode}")

  s_json = Path(context.actions_path).read_text(encoding='utf-8')
  config = SetupConfig.model_validate_json(s_json)

  for index, step in enumerate(config.steps):
    step_context = StepContext(index, config.steps, context)
    if not step_context.is_qualified():
      continue
    if step.action == StepAction.PULL:
      handle_pull(step_context)
    elif step.action == StepAction.DOWNLOAD:
      handle_download(step_context)
    elif step.action == StepAction.EXTRACT:
      handle_extract(step_context)
    elif step.action == StepAction.GENENVSCRIPT:
      handle_env_script(step_context)
    elif step.action == StepAction.GITCMD:
      handle_gitcmd(step_context)
