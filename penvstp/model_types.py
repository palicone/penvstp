from penvstp.helpers import get_filename_without_extension
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os

class StepAction(str, Enum):
  PULL = "pull"
  GITCMD = "gitcmd"
  DOWNLOAD = "download"
  EXTRACT = "extract"
  GENENVSCRIPT = "generate_env_script"

class HostArch(str, Enum):
  WindowsX64 = "WindowsX64"
  LinuxX64 = "LinuxX64"
  LinuxAArch64 = "LinuxAArch64"

class RunType(str, Enum):
  DEFAULT = "default"
  '''
  Refresh if needed
  '''
  CHECKSRC = "checksrc"
  '''
  Only check if source resources are available
  '''
  CHECK = "check"
  '''
  Check if resources are available and in place
  '''
  FORCE = "force"
  '''
  Perform all actions even if resources are in place
  '''

class RunMode(str, Enum):
  DEFAULT = "default"
  '''
  Perform actions as needed and requested by RunType
  '''
  DRY_NOSRC = "dry_nosrc"
  '''
  Assume action source is missing
  '''
  DRY_NODST = "dry_nodst"
  '''
  Assume action source is available
  Assume action destination doesn't exist
  '''
  DRY_STALEDST = "dry_staledst"
  '''
  Assume action source is available
  Assume action destination is not up to date
  '''
class StepParams(BaseModel):
  url: Optional[str] = None
  env_vars: Optional[List[Dict[str, str]]] = None
  output_name: Optional[str] = None
  reference_id: Optional[str] = None
  cmd: Optional[str] = None


class SetupStep(BaseModel):
  id: Optional[str] = None
  architectures: Optional[List[HostArch]] = Field(default_factory=list)
  action: str
  params: StepParams


class SetupConfig(BaseModel):
  steps: List[SetupStep]

class ExecutionContext:
  def __init__(self, host_arch: HostArch, actions_path: str, temp_folder: str, tools_folder: str, externals_folder: str, run_type: RunType, run_mode: RunMode):
    self.host_arch = host_arch
    self.actions_path = actions_path
    self.temp_folder = temp_folder
    self.tools_folder = tools_folder
    self.externals_folder = externals_folder
    self.run_type = run_type
    self.run_mode = run_mode

  def is_run_type(self, run_type: RunType)->bool:
    return self.run_type == run_type

  def is_check_only(self)->bool:
    if self.is_run_type(RunType.CHECKSRC):
      return True
    if self.is_run_type(RunType.CHECK):
      return True
    return False

  def is_want_dst(self)->bool:
    if self.is_run_type(RunType.CHECKSRC):
      return False
    return False

  def is_force(self)->bool:
    return self.is_run_type(RunType.FORCE)

  def is_dry(self)->bool:
    return self.run_mode != RunMode.DEFAULT

  def is_dry_src(self)->bool:
    return self.run_mode != RunMode.DRY_NOSRC

  def is_dry_dest(self)->bool:
    return self.run_mode != RunMode.DRY_NODST

  def is_dry_stale(self)->bool:
    if self.is_dry_dest():
      return self.run_mode != RunMode.DRY_STALEDST
    return False

class StepContext:
  def __init__(self, step_index:int, all_steps:List[SetupStep], configuration:ExecutionContext):
    self._step_index = step_index
    self._all_steps:List[SetupStep] = all_steps
    self._configuration:ExecutionContext = configuration
  def step(self) -> SetupStep:
    return self._all_steps[self._step_index]
  def configuration(self) -> ExecutionContext:
    return self._configuration
  def all_steps(self) -> List[SetupStep]:
    return self._all_steps
  def is_action(self, action_name:str) -> bool:
    return self.step().action == action_name
  def index(self) -> int:
    return self._step_index

  def is_qualified(self):
    if not self.step().architectures:
      return True
    if self.configuration().host_arch in self.step().architectures:
      return True
    return False

  def get_id(self) -> str:
    return self._all_steps[self._step_index].id

  def id_matches(self, other_id: str) -> bool:
    own_id = self.get_id()
    if not own_id:
      return False
    return other_id == own_id

  def get_step_by_id(self, step_id: str):
    for i, step in enumerate(self._all_steps):
      step_ctx = StepContext(i, self._all_steps, self._configuration)
      if not step_ctx.is_qualified():
        continue
      if step_ctx.id_matches(step_id):
        return  step_ctx
    return None

  def get_ref_step(self):
    if self.step().params.reference_id:
      return self.get_step_by_id(self.step().params.reference_id)
    return None

  def get_action(self) -> str:
    return self.step().action

  # Don't search for references. Only return own dest folder
  def get_destination_folder(self) -> Optional[str]:
    if self.get_action() == StepAction.PULL:
      filename = os.path.basename(self.step().params.url)
      return os.path.join(self.configuration().externals_folder, filename)
    elif self.get_action() == StepAction.GITCMD:
      pass
    elif self.get_action() == StepAction.DOWNLOAD:
      return self.configuration().temp_folder
    elif self.get_action() == StepAction.EXTRACT:
      folder = self._configuration.tools_folder
      src = self.get_ref_step().get_destination_file()
      src = get_filename_without_extension(src)
      return os.path.join(folder, src)
    elif self.get_action() == StepAction.GENENVSCRIPT:
      pass
    else:
      raise RuntimeError(f"Unhandled action: {self.get_action()}")
    return None

  # Don't search for references. Only return own dest
  def get_destination_file(self) -> Optional[str]:
    if self.get_action() == StepAction.PULL:
      pass
    elif self.get_action() == StepAction.GITCMD:
      pass
    elif self.get_action() == StepAction.DOWNLOAD:
      folder = self.get_destination_folder()
      filename = os.path.basename(self.step().params.url)
      return os.path.join(folder, filename)
    elif self.get_action() == StepAction.EXTRACT:
      pass
    elif self.get_action() == StepAction.GENENVSCRIPT:
      pass
    else:
      raise RuntimeError(f"Unhandled action: {self.get_action()}")
    return None
