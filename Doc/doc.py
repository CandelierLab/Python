import os
import shutil

# === Parameters ===========================================================

outDir = 'Doc/html'

erase = True

# ==========================================================================

# --- Command preparation --------------------------------------------------

cmd = 'pdoc --math'

for root, subdirs, files in os.walk('AE'):
  print(root)


cmd += ' AE -o ' + outDir

# --- Execution ------------------------------------------------------------

# Remove previous folder
if erase and os.path.exists(outDir):
  shutil.rmtree(outDir)

print(cmd)

# os.system(cmd)

