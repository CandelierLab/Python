import os
import shutil

os.system('clear')

# === Parameters ===========================================================

outDir = 'Doc/html'

erase = True

# ==========================================================================

# --- Command preparation --------------------------------------------------

cmd = 'pdoc --math AE '

for root, subdirs, files in os.walk('AE'):
  print(root)


cmd += 'AE/Display -o ' + outDir

# --- Execution ------------------------------------------------------------

# Remove previous folder
if erase and os.path.exists(outDir):
  shutil.rmtree(outDir)

print(cmd)

os.system(cmd)

