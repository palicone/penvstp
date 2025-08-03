import argparse
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
  print(f"This __file__: {__file__}")
  default_root = os.getcwd()
  parser = argparse.ArgumentParser(description="Environment Setup Script")
  parser.add_argument("--host-arch", required=False, choices=[arch.value for arch in HostArch], help="Target host architecture")
  parser.add_argument("--temp-folder", required=False, default=os.path.join(default_root, "temp"))
  parser.add_argument("--tools-folder", required=False, default=os.path.join(default_root, "tools"))
  parser.add_argument("--externals-folder", required=False, default=os.path.join(default_root, "externals"))
  parser.add_argument("--run-mode", required=False, default="default", choices=[t.value for t in RunMode], help="Run mode: default, checksrc, check, force")
  parser.add_argument("--dry-mode", required=False, default="default", choices=[t.value for t in DryMode], help="Dry mode: default, nosrc, nodst, staledst")
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
                             RunMode(args.run_mode),
                             DryMode(args.dry_mode))
  process_steps(context)

if __name__ == "__main__":
  main()
