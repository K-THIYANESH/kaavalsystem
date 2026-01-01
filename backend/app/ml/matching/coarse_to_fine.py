"""Coarse-to-fine matching with FAISS integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Any
from pathlib import Path
import numpy as np
import faiss
import pickle

from .narrowing import AttributeFilter
from ...core.config import settings


@dataclass
class MatchCandidate:
    person_id: int
    score: float
    attribute_score: float = 0.0
    person_name: str | None = None


@dataclass
class CoarseToFineMatcher:
    """Encapsulate FAISS-based similarity search with attribute filtering."""

    faiss_index_path: str | None = None
    attribute_filter: AttributeFilter = field(default_factory=AttributeFilter)
    _index: Any = field(default=None, init=False, repr=False)
    _metadata: dict = field(default_factory=dict, init=False, repr=False)
    _loaded: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        """Load FAISS index on initialization."""
        self._load_index()

    def _load_index(self):
        """Load FAISS index and metadata from disk."""
        try:
            # Determine index path
            if self.faiss_index_path:
                index_path = Path(self.faiss_index_path)
            else:
                index_path = settings.models_dir / "faiss" / "embeddings.index"
            
            metadata_path = index_path.parent / "metadata.pkl"
            
            # Check if index exists
            if not index_path.exists():
                print(f"[WARNING] FAISS index not found at {index_path}")
                print("Run: python scripts/build_faiss_index.py")
                self._loaded = False
                return
            
            # Load FAISS index
            self._index = faiss.read_index(str(index_path))
            print(f"✅ Loaded FAISS index from {index_path} ({self._index.ntotal} embeddings)")
            
            # Load metadata
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self._metadata = pickle.load(f)
                print(f"✅ Loaded metadata: {self._metadata.get('n_embeddings')} embeddings, "
                      f"dimension {self._metadata.get('dimension')}")
            
            self._loaded = True
            
        except Exception as e:
            print(f"[ERROR] Failed to load FAISS index: {e}")
            self._loaded = False

    def coarse_filter(self, embedding: Sequence[float], candidate_ids: List[int] | None = None) -> List[int]:
        """
        Perform FAISS-based similarity search.
        
        Args:
            embedding: Query embedding vector
            candidate_ids: Optional list of candidate IDs to filter (not yet implemented)
            
        Returns:
            List of person IDs from top matches
        """
        if not self._loaded or self._index is None:
            # Fallback to mock if index not loaded
            if candidate_ids:
                return candidate_ids[:500]
            return list(range(1, 501))
        
        # Convert embedding to numpy array and normalize
        query = np.array(embedding, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(query)
        
        # Search for top-k matches
        k = min(500, self._index.ntotal)
        distances, indices = self._index.search(query, k)
        
        # Convert indices to person IDs using metadata
        person_ids = []
        if 'person_ids' in self._metadata:
            for idx in indices[0]:
                if 0 <= idx < len(self._metadata['person_ids']):
                    person_ids.append(self._metadata['person_ids'][idx])
        else:
            # Fallback: assume index position = person_id
            person_ids = indices[0].tolist()
        
        # Filter by candidate_ids if provided
        if candidate_ids:
            person_ids = [pid for pid in person_ids if pid in candidate_ids]
        
        return person_ids

    def fine_match(self, embedding: Sequence[float], candidate_ids: List[int]) -> List[MatchCandidate]:
        """
        Perform fine-grained matching with re-ranking.
        
        Args:
            embedding: Query embedding vector
            candidate_ids: List of candidate person IDs
            
        Returns:
            List of MatchCandidate objects sorted by score
        """
        if not self._loaded or self._index is None:
            # Fallback to mock implementation
            rng = np.random.default_rng()
            matches = []
            for person_id in candidate_ids[:10]:
                score = float(rng.uniform(0.8, 0.95))
                attribute = float(rng.uniform(0.7, 0.9))
                matches.append(MatchCandidate(person_id=person_id, score=score, attribute_score=attribute))
            matches.sort(key=lambda c: c.score, reverse=True)
            return matches
        
        # Convert embedding to numpy array and normalize
        query = np.array(embedding, dtype=np.float32).reshape(1, -1)
        faiss.normalize_L2(query)
        
        # Get indices for candidate_ids
        person_id_to_idx = {}
        if 'person_ids' in self._metadata:
            for idx, pid in enumerate(self._metadata['person_ids']):
                person_id_to_idx[pid] = idx
        
        # Search only among candidates
        matches = []
        candidate_indices = [person_id_to_idx.get(pid, -1) for pid in candidate_ids if pid in person_id_to_idx]
        
        if not candidate_indices:
            return []
        
        # For each candidate, compute similarity
        for idx, person_id in zip(candidate_indices, candidate_ids):
            if idx < 0 or idx >= self._index.ntotal:
                continue
            
            # Get embedding from index
            candidate_emb = self._index.reconstruct(int(idx)).reshape(1, -1)
            
            # Compute similarity (inner product after normalization = cosine similarity)
            similarity = float(np.dot(query, candidate_emb.T)[0, 0])
            
            matches.append(MatchCandidate(
                person_id=person_id,
                score=similarity,
                attribute_score=0.0
            ))
        
        # Sort by score
        matches.sort(key=lambda c: c.score, reverse=True)
        return matches[:10]  # Return top 10

    def match_with_attributes(
        self, 
        embedding: Sequence[float], 
        attributes: dict[str, Any] | None = None,
        tolerance: str = "strict"
    ) -> List[MatchCandidate]:
        """
        Perform matching with optional attribute pre-filtering.
        
        Args:
            embedding: Query embedding vector
            attributes: Optional attributes for pre-filtering
            tolerance: Tolerance level for attribute matching
            
        Returns:
            List of MatchCandidate objects
        """
        candidate_ids = None
        
        # 1. Attribute Narrowing
        if attributes:
            candidate_ids = self.attribute_filter.filter_candidates(attributes, tolerance)
            if not candidate_ids:
                return []  # No matches found with these attributes
        
        # 2. Coarse Filter (Vector Search)
        filtered_ids = self.coarse_filter(embedding, candidate_ids)
        
        # 3. Fine Match (Re-ranking)
        return self.fine_match(embedding, filtered_ids)
