"""Read a FreeSpace .vp archive.

usage: vpx.py <vp> <outdir or -> [substring...]
With "-", list the files; else extract the files whose path contains a substring.
"""
import os
import struct
import sys


def read_vp(vp):
    """Yield (path, offset, size) for each file in the archive."""
    with open(vp, "rb") as f:
        sig, _ver, off, n = struct.unpack("<4siii", f.read(16))
        assert sig == b"VPVP", vp
        f.seek(off)
        ents = [struct.unpack("<ii32si", f.read(44)) for _ in range(n)]
    path = []
    for o, s, name, t in ents:
        name = name.split(b"\0")[0].decode("latin1")
        if name == "..":
            path.pop()
        elif s == 0 and t == 0:  # a directory entry
            path.append(name)
        else:
            yield "/".join(path + [name]), o, s


if __name__ == "__main__":
    vp, out, pats = sys.argv[1], sys.argv[2], [p.lower() for p in sys.argv[3:]]
    with open(vp, "rb") as f:
        for p, o, s in read_vp(vp):
            if pats and not any(x in p.lower() for x in pats):
                continue
            if out == "-":
                print(p, s)
                continue
            dst = os.path.join(out, p)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            f.seek(o)
            with open(dst, "wb") as d:
                d.write(f.read(s))
