import sys
from pathlib import Path
proj = Path(__file__).resolve().parents[2]
if str(proj) not in sys.path:
    sys.path.insert(0, str(proj))

try:
    import torch
    from app.core.model_utils import safe_torch_load

    # Try to register safe globals if torch_utils is available
    try:
        from torch_utils.persistence import _reconstruct_persistent_obj
        try:
            torch.serialization.add_safe_globals([_reconstruct_persistent_obj])
        except Exception:
            pass
    except Exception:
        pass

    path = proj / 'backend' / 'models' / 'stylegan2_age.pt'
    print('Loading checkpoint:', path)

    # Prefer weights-only safe load, then allow full load via the same helper
    obj = safe_torch_load(path, map_location='cpu')
    if obj is None:
        # Try again but allow full unpickle explicitly
        obj = safe_torch_load(path, map_location='cpu', prefer_weights_only=False, allow_untrusted=True)

    if obj is None:
        print('Failed to load checkpoint (both safe and fallback attempts returned None)')
    else:
        print('Loaded object type:', type(obj))

except Exception:
    import traceback
    traceback.print_exc()
