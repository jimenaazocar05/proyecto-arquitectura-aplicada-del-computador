import urllib.request
import sys

def rep(count, block_size, total_size):
    sys.stdout.write(f'\r{count * block_size / 1024 / 1024:.2f}MB / {total_size / 1024 / 1024:.2f}MB')
    sys.stdout.flush()

urllib.request.urlretrieve('https://files.pythonhosted.org/packages/a2/50/59227d06bdc96e23322713c381af4e77420949d8cd8a042c79e0043096cc/llvmlite-0.47.0-cp311-cp311-win_amd64.whl', 'llvmlite-0.47.0-cp311-cp311-win_amd64.whl', rep)
print("\nDone")
