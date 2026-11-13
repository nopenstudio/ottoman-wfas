import os

# Point export_dir to the folder you will be keeping your module
# Make sure you use forward slashes (/) and NOT backward slashes (\)

#export_dir = "c:/MiB-OiM/MiB-New World/MiB-New World/Build/Modules/Ogniem i Mieczem/"
#export_dir = "c:/MiB-OiM/Mount&Blade/SBL-OiM/build_dlc/Modules/Ogniem i Mieczem/"
export_dir = os.environ.get("WFAS_EXPORT_DIR", "c:/Program Files (x86)/Steam/steamapps/common/Mount & Blade With Fire and Sword/Modules/OTTOMAN/")
if not export_dir.endswith("/"):
  export_dir += "/"
