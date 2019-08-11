import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

BUFSIZE = 2 << 10
TMP_FILE_EXTENSION = ".tmp"


def unlock(full_filename):
	full_filename = full_filename.strip()
	print(f"unlocking {full_filename}")
	tmp_filename = f"{full_filename}{TMP_FILE_EXTENSION}"
	try:
		with open(full_filename, "rb") as rf:
			with open(tmp_filename, "wb") as wf:
				buf = rf.read(BUFSIZE)
				while buf:
					wf.write(buf)
					buf = rf.read(BUFSIZE)
		os.remove(full_filename)
		subprocess.run(["mv", tmp_filename, full_filename])
	except FileNotFoundError:
		return


def main():
	if len(sys.argv) > 1:
		for arg in sys.argv[1:]:
			unlock(arg)
	else:
		executor = ThreadPoolExecutor()
		for _ in executor.map(unlock, sys.stdin):
			pass


if __name__ == "__main__":
	main()
