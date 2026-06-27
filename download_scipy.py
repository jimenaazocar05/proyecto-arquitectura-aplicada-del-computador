import urllib.request
import sys

def rep(count, block_size, total_size):
    sys.stdout.write(f'\r{count * block_size / 1024 / 1024:.2f}MB / {total_size / 1024 / 1024:.2f}MB')
    sys.stdout.flush()

urllib.request.urlretrieve('https://files.pythonhosted.org/packages/95/da/0d1df507cf574b3f224ccc3d45244c9a1d732c81dcb26b1e8a766ae271a8/scipy-1.17.1-cp311-cp311-win_amd64.whl', 'scipy.whl', rep)
print("\nDone")
