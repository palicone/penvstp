import argparse
from penvstp.helpers import *
from penvstp.model_types import *
from penvstp.main import process_steps
import platform

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

def main():
  default_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
  parser = argparse.ArgumentParser(description="Environment Setup Script")
  parser.add_argument("--host-arch", required=False, choices=[arch.value for arch in HostArch],
                      help="Target host architecture")
  parser.add_argument("--temp-folder", required=False, default=os.path.join(default_root, "temp"))
  parser.add_argument("--tools-folder", required=False, default=os.path.join(default_root, "tools"))
  parser.add_argument("--externals-folder", required=False, default=os.path.join(default_root, "externals"))
  parser.add_argument("--run-type", required=False, default="default", choices=[t.value for t in RunType], help="Run type: default, check, force")
  parser.add_argument("--run-mode", required=False, default="default", choices=[t.value for t in RunMode], help="Run mode: default, dry_nosrc, dry_nodst, dry_staledst")
  parser.add_argument('input_file', type=str, help='Path to the input file to process')
  args = parser.parse_args()
  host_arch = HostArch(args.host_arch) if args.host_arch else detect_host_arch()
  if args.host_arch and host_arch != detect_host_arch():
    raise RuntimeError(f"Given architecture '{args.host_arch}' does not match detected '{detect_host_arch().value}'")
  context = ExecutionContext(host_arch,
                             args.input_file,
                             args.temp_folder,
                             args.tools_folder,
                             args.externals_folder,
                             RunType(args.run_type),
                             RunMode(args.run_mode))
  process_steps(context)

if __name__ == "__main__":
  main()
