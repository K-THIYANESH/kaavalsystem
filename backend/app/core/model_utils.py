"""Model loading utilities to reduce unsafe unpickling and centralize torch.load behavior."""

from __future__ import annotations

from pathlib import Path
import torch
from typing import Any, Optional


def safe_torch_load(path: Path | str, map_location: Optional[str | torch.device] = None, prefer_weights_only: bool = True, allow_untrusted: bool = False) -> Any:
        """Attempt to load a torch checkpoint safely.

        Behavior:
        - If `prefer_weights_only` is True (default), first try `torch.load(..., weights_only=True)`
            which avoids unpickling arbitrary objects.
        - If that fails and `allow_untrusted` is False, return `None` instead of performing
            a full unpickling load. This prevents accidental execution of untrusted pickle data.
        - If `allow_untrusted` is True or `prefer_weights_only` is False, perform a full
            `torch.load(..., weights_only=False)` as a last resort.

        Returns the loaded object, or `None` if no safe load was possible and untrusted
        loading was not requested.
        """
    p = Path(path)
    if map_location is None:
        map_location = 'cpu'

    # Try weights_only first
    if prefer_weights_only:
        try:
            return torch.load(str(p), map_location=map_location, weights_only=True)
        except TypeError:
            # weights_only not supported
            pass
        except Exception:
            # weights_only attempted but failed; do not automatically fall back
            # to full unpickle unless explicitly allowed by the caller.
            if not allow_untrusted:
                return None

    # If caller requested a full unpickle path, allow it explicitly
    if allow_untrusted or not prefer_weights_only:
        return torch.load(str(p), map_location=map_location)

    # If we reach here, we did not perform a full load and weights-only failed
    return None
