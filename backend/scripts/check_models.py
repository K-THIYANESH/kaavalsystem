import pathlib
import sys

print('PYTHON:', sys.executable)
base = pathlib.Path(__file__).resolve().parents[1] / 'models'
print('MODELS DIR:', base)

import importlib
import sys
from pathlib import Path as _Path

# Check ONNX runtime
try:
    import onnxruntime as ort
    print('onnxruntime version:', ort.__version__)
except Exception as e:
    print('onnxruntime import failed:', e)

# Check torch
try:
    import torch
    print('torch version:', torch.__version__)
except Exception as e:
    print('torch import failed:', e)

files = {
    'retinaface': base / 'retinaface.onnx',
    'arcface': base / 'arcface_resnet100.onnx',
    'attribute': base / 'attribute_net.onnx',
    'gfpgan': base / 'gfpgan.pth',
    'stylegan': base / 'stylegan2_age.pt',
}

for name, path in files.items():
    if not path.exists():
        print(f'MISSING: {name} -> {path}')
        continue
    print(f'FOUND: {name} -> {path} (size={path.stat().st_size})')
    if path.suffix == '.onnx':
        try:
            sess = ort.InferenceSession(str(path))
            print(f'Loaded ONNX model for {name} OK')
        except Exception as e:
            print(f'Failed to load ONNX {name}:', e)
    else:
        try:
            import torch
            # Ensure project root is on sys.path so training runtime helpers
            # (e.g. torch_utils) can be imported during unpickling.
            try:
                project_root = _Path(__file__).resolve().parents[3]
                pr = str(project_root)
                if pr not in sys.path:
                    sys.path.insert(0, pr)
            except Exception:
                pass

            # If checkpoint needs torch_utils-specific unpickling helpers,
            # attempt to register safe globals so torch.load can reconstruct.
            if name == 'stylegan':
                try:
                    from torch_utils.persistence import _reconstruct_persistent_obj
                    try:
                        torch.serialization.add_safe_globals([_reconstruct_persistent_obj])
                    except Exception:
                        pass
                except Exception:
                    # torch_utils not importable yet; we'll still try to load
                    pass

            try:
                from app.core.model_utils import safe_torch_load
            except Exception:
                # fallback to a local safe_torch_load implementation
                def safe_torch_load(p, map_location='cpu', prefer_weights_only=True):
                    try:
                        # Try weights-only first if available
                        try:
                            return torch.load(str(p), map_location=map_location, weights_only=True)
                        except TypeError:
                            # weights_only not supported; try full load
                            return torch.load(str(p), map_location=map_location)
                        except Exception:
                            # final fallback: full load
                            return torch.load(str(p), map_location=map_location)
                    except Exception:
                        return None

            try:
                obj = safe_torch_load(path, map_location='cpu')
                print(f'Torch load for {name} OK; type={type(obj)}')
            except Exception as e:
                print(f'Failed to torch.load {name}:', e)

        except Exception as e:
            print(f'Failed to torch.load {name}:', e)

print('MODEL CHECK COMPLETE')
