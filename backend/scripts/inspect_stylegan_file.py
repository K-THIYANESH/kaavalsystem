import sys
from pathlib import Path
import binascii

proj = Path(__file__).resolve().parents[2]
path = proj / 'backend' / 'models' / 'stylegan2_age.pt'
print('Path:', path)
print('Exists:', path.exists())
if not path.exists():
    sys.exit(2)
size = path.stat().st_size
print('Size bytes:', size)
with open(path, 'rb') as f:
    head = f.read(512)
print('First 64 bytes (hex):', binascii.hexlify(head[:64]).decode('ascii'))
print('First 128 bytes (ascii subset):')
print(''.join([c if 32 <= c < 127 else '.' for c in head[:128]]))

# Try detecting common container types
if head.startswith(b'PK'):
    print('File looks like a zip (PK)')
if head.startswith(b"\x7fELF"):
    print('File looks like an ELF binary')
if head.startswith(b'\x89PNG'):
    print('File looks like a PNG')

# Try torch.jit.load and torch.load attempts
try:
    import torch
    print('torch version:', torch.__version__)
    try:
        print('Trying torch.jit.load...')
        m = torch.jit.load(str(path), map_location='cpu')
        print('torch.jit.load succeeded, type:', type(m))
    except Exception as e:
        print('torch.jit.load failed:', repr(e))
    try:
        print('Trying safe_torch_load...')
        from app.core.model_utils import safe_torch_load
        m = safe_torch_load(path, map_location='cpu')
        print('safe_torch_load succeeded, type:', type(m))
    except Exception as e:
        print('safe_torch_load failed:', repr(e))

    try:
        print('Trying safe_torch_load fallback (allow full unpickle)...')
        from app.core.model_utils import safe_torch_load
        m = safe_torch_load(path, map_location='cpu', prefer_weights_only=False, allow_untrusted=True)
        print('safe_torch_load (fallback) succeeded, type:', type(m))
    except Exception as e:
        print('safe_torch_load (fallback) failed:', repr(e))
except Exception as e:
    print('Torch import failed:', repr(e))

print('Done')
