import os
import shutil

os.system('clear')

# === Parameters ===========================================================

outDir = 'Doc/html'

erase = True

# ==========================================================================

# --- Command preparation --------------------------------------------------

# May be required to suppress warnings:
# export PDOC_ALLOW_EXEC=1

cmd = 'pdoc --docformat google --math '

for root, subdirs, files in os.walk('AE'):
  if '__pycache__' not in root:
    cmd += root + ' '

for root, subdirs, files in os.walk('Examples'):
  if '__pycache__' not in root:
    cmd += root + ' '

cmd += '-o ' + outDir

# --- Execution ------------------------------------------------------------

# Remove previous folder
if erase and os.path.exists(outDir):
  shutil.rmtree(outDir)

# print(cmd)

os.system(cmd)

