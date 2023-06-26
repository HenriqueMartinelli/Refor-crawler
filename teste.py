import psutil
import subprocess
from subprocess import PIPE
teste=1
process = subprocess.Popen(f"google-chrome https://google.com.br?search={teste}", shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
pid = process.pid
