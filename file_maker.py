import os

sizes = [8,64,512,4096,32768,262144,2097152]

for s in sizes:
    with open(f"file_{s}.bin","wb") as f:
        f.write(os.urandom(s))