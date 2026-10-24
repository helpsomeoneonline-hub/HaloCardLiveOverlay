"""Safely decode the private Android signing bundle from GitHub Actions secrets."""
import base64
import io
import os
from pathlib import Path
import re
import sys
import tarfile

raw = os.environ.get("HALOCARD_SIGNING_BUNDLE_B64", "")
output = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "halocard-signing"
output.mkdir(parents=True, exist_ok=True)

candidates = ["".join(raw.split())]
candidates.extend(re.findall(r"[A-Za-z0-9+/]{128,}={0,2}", raw))
for candidate in candidates:
    try:
        decoded = base64.b64decode(candidate, validate=True)
        if decoded[:2] != bytes([31, 139]):
            continue
        with tarfile.open(fileobj=io.BytesIO(decoded), mode="r:gz") as archive:
            contents = {}
            for name in ("halocard-release.jks", "signing-pass.txt"):
                handle = archive.extractfile(name)
                if handle is None:
                    raise ValueError("missing signing component")
                contents[name] = handle.read()
            if not contents["halocard-release.jks"] or not contents["signing-pass.txt"]:
                raise ValueError("empty signing component")
            for name, data in contents.items():
                (output / name).write_bytes(data)
        print("Permanent signing bundle decoded and both signing files validated.")
        break
    except Exception:
        continue
else:
    sys.exit("SIGNING_SECRET_INVALID: Replace GitHub secret HALOCARD_SIGNING_BUNDLE_B64 with the entire contents of HaloCard_GitHub_Secret_Value.txt. Do not paste the filename or a ZIP archive.")
