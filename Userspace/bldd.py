import os
import sys
import json
import time
import lief
import argparse
import warnings


X86_arch = {}
X86_64_arch = {}
ARM_arch = {}
AARCH64_arch = {}
Unknown_arch = {}
json_report = {
    "architectures": {}
}

# Check if a file is an ELF file
def is_elf_file(file_path):
  try:
    with open(file_path, "rb") as f:
        magic = f.read(4)
    return magic == b'\x7fELF'
  except Exception:
      return False

# Get the data from the ELF file found in the directory
def get_data(filename_path, elf):
  arch_type = elf.header.machine_type

  # Arch X86
  if arch_type == lief.ELF.ARCH.I386:
    for i in elf.dynamic_entries:
        try:
          if i.tag == lief.ELF.DynamicEntry.TAG.NEEDED:
              if str(i.name) not in X86_arch:
                  X86_arch[str(i.name)] = {'file_path': []}
              X86_arch[str(i.name)]['file_path'].append(filename_path)
        except Exception:
          print(f"Error in file: {filename_path}")

  # Arch X86_64
  elif arch_type == lief.ELF.ARCH.X86_64:
    for i in elf.dynamic_entries:
        try:
          if i.tag == lief.ELF.DynamicEntry.TAG.NEEDED:
              if str(i.name) not in X86_64_arch:
                  X86_64_arch[str(i.name)] = {'file_path': []}
              X86_64_arch[str(i.name)]['file_path'].append(filename_path)
        except Exception:
          print(f"Error in file: {filename_path}")

  # Arch ARM
  elif arch_type == lief.ELF.ARCH.ARM:
    for i in elf.dynamic_entries:
        try:
          if i.tag == lief.ELF.DynamicEntry.TAG.NEEDED:
              if i.name not in ARM_arch:
                  ARM_arch[i.name] = {'file_path': []}
              ARM_arch[i.name]['file_path'].append(filename_path)
        except Exception:
          print(f"Error in file: {filename_path}")

  # Arch AARCH64
  elif arch_type == lief.ELF.ARCH.AARCH64:
    for i in elf.dynamic_entries:
        try:
          if i.tag == lief.ELF.DynamicEntry.TAG.NEEDED:
              if i.name not in AARCH64_arch:
                  AARCH64_arch[i.name] = {'file_path': []}
              AARCH64_arch[i.name]['file_path'].append(filename_path)
        except Exception:
          print(f"Error in file: {filename_path}")

  # Unknown Arch
  else:
    for i in elf.dynamic_entries:
      try:
        if i.tag == lief.ELF.DynamicEntry.TAG.NEEDED:
          if i.name not in Unknown_arch:
              Unknown_arch[i.name] = {'file_path': []}
          Unknown_arch[i.name]['file_path'].append(filename_path)
      except Exception:
        print(f"Error in file: {filename_path}")

# Traverse through the files in the directory
def traverse_files(directory):
  global X86_arch, X86_64_arch, ARM_arch, AARCH64_arch, Unknown_arch
  for dirpath, _, filenames in os.walk(directory, topdown=True):
    for filename in filenames:
        filename_path = os.path.join(dirpath, filename)
        if os.access(filename_path, os.X_OK) and is_elf_file(filename_path):
          try:
            elf: lief.ELF.Binary = lief.ELF.parse(filename_path)
          except Exception:
            print(f"Error parsing file: {filename_path}")
          get_data(filename_path, elf)

  X86_arch = dict( sorted(X86_arch.items(), key=lambda item: len(item[1]["file_path"]), reverse=True))
  X86_64_arch = dict( sorted(X86_64_arch.items(), key=lambda item: len(item[1]["file_path"]), reverse=True))
  ARM_arch = dict( sorted(ARM_arch.items(), key=lambda item: len(item[1]["file_path"]), reverse=True))
  AARCH64_arch = dict( sorted(AARCH64_arch.items(), key=lambda item: len(item[1]["file_path"]), reverse=True))
  Unknown_arch = dict( sorted(Unknown_arch.items(), key=lambda item: len(item[1]["file_path"]), reverse=True))



# Print the findings
def print_data(dictionary, need_json=False):

  print(f"Report on dynamic used libraries by ELF executables on {dictionary}\n")z

  # X86
  print("==========I386(x86)==========\n")
  json_report["architectures"]["X86"] = {}
  for key, value in X86_arch.items():
      print(f"{key} ({len(value.get('file_path'))} files)")
      print("==============================Files==============================\n")
      for i in value.get('file_path'):
          print(f"  -> {i}")
      print("==================================================================\n")
      json_report["architectures"]["X86"][key] = {
      "file_count": len(value.get("file_path", [])),
      "files": value.get("file_path", [])
      }

  # X86_64
  print("==========X86_64==========\n")
  json_report["architectures"]["X86_64"] = {}
  for key, value in X86_64_arch.items():
      print(f"{key} ({len(value.get('file_path'))} files)")
      print("==============================Files==============================\n")
      for i in value.get('file_path'):
          print(f"  -> {i}")
      print("==================================================================\n")
      json_report["architectures"]["X86_64"][key] = {
      "file_count": len(value.get("file_path", [])),
      "files": value.get("file_path", [])
      }

  # ARM
  print("==========ARM==========\n")
  json_report["architectures"]["ARM"] = {}
  for key, value in ARM_arch.items():
      print(f"{key} ({len(value.get('file_path'))} files)")
      print("==============================Files==============================\n")
      for i in value.get('file_path'):
          print(f"  -> {i}")
      print("==================================================================\n")
      json_report["architectures"]["ARM"][key] = {
      "file_count": len(value.get("file_path", [])),
      "files": value.get("file_path", [])
      }

  # AARCH64
  print("==========AARCH64==========\n")
  json_report["architectures"]["AARCH64"] = {}
  for key, value in AARCH64_arch.items():
      print(f"{key} ({len(value.get('file_path'))} files)")
      print("==============================Files==============================\n")
      for i in value.get('file_path'):
          print(f"  -> {i}")
      print("==================================================================\n")
      json_report["architectures"]["AARCH64"][key] = {
      "file_count": len(value.get("file_path", [])),
      "files": value.get("file_path", [])
      }

  # Unknown
  print("==========Unknown==========\n")
  json_report["architectures"]["Unknown"] = {}
  for key, value in Unknown_arch.items():
      print(f"{key} ({len(value.get('file_path'))} files)")
      for i in value.get('file_path'):
          print(f"  -> {i}")
      json_report["architectures"]["Unknown"][key] = {
      "file_count": len(value.get("file_path", [])),
      "files": value.get("file_path", [])
      }

  if need_json:
    with open("bldd_report.json", "w") as f:
      json.dump(json_report, f, indent=4)


def print_data_txt(directory):
  txt_output = sys.stdout
  txt_file = open("bldd_report.txt", "w")
  sys.stdout = txt_file
  print_data(directory)
  sys.stdout = txt_output
  txt_file.close()


def main():

  parser = argparse.ArgumentParser(description='''This script will traverse through all
    the files in the specified directory and print the dynamic libraries used by ELF executables''')
  parser.add_argument('-d', help='Directory to traverse through', required=True)
  parser.add_argument('--json', help='Output the report in JSON format', action='store_true')
  parser.add_argument('--txt', help='Output the report in TXT format', action='store_true')
  arg = parser.parse_args()
  dir = arg.d
  need_json = arg.json
  need_txt = arg.txt
  warnings.filterwarnings("ignore", category=RuntimeWarning)
  lief.logging.set_level(lief.logging.LEVEL.CRITICAL)

  traverse_files(dir)

  # time_start = time.time()
  if need_txt:
    print_data_txt(dir)

  print_data(dir, need_json)
  # time_end = time.time()
  # print(f"Time taken: {time_end - time_start} seconds")

if __name__ == "__main__":
    main()