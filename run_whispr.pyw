"""Launcher for Whispr."""
import sys, os
from pathlib import Path
root = Path(__file__).resolve().parent
cublas = root / ".venv/Lib/site-packages/nvidia/cublas/bin"
cudnn = root / ".venv/Lib/site-packages/nvidia/cudnn/bin"
os.environ["PATH"] = str(cublas) + os.pathsep + str(cudnn) + os.pathsep + os.environ["PATH"]
sys.path.insert(0, str(root))
from whispr.app import main
main()
