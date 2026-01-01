"""Metrics Collection Module.

Tracks performance and quality metrics for the KAAVAL system.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np


@dataclass
class MetricPoint:
    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects and aggregates system metrics."""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics: Dict[str, deque] = {}

    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = deque(maxlen=self.history_size)
        
        self.metrics[name].append(
            MetricPoint(timestamp=time.time(), value=value, tags=tags or {})
        )

    def get_average(self, name: str, window_seconds: int = 60) -> float:
        """Get average value of a metric over the last window_seconds."""
        if name not in self.metrics:
            return 0.0
        
        now = time.time()
        cutoff = now - window_seconds
        
        values = [m.value for m in self.metrics[name] if m.timestamp > cutoff]
        if not values:
            return 0.0
        
        return float(np.mean(values))

    def get_latest(self, name: str) -> float:
        """Get the most recent value."""
        if name not in self.metrics or not self.metrics[name]:
            return 0.0
        return self.metrics[name][-1].value

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of all metrics."""
        summary = {}
        for name in self.metrics:
            summary[name] = {
                "latest": self.get_latest(name),
                "avg_1min": self.get_average(name, 60),
                "avg_5min": self.get_average(name, 300),
                "count": len(self.metrics[name])
            }
        return summary


# Global collector instance
metrics = MetricsCollector()


def record_latency(name: str):
    """Decorator to record function latency."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = (time.time() - start) * 1000  # ms
                metrics.record(f"{name}_latency_ms", duration)
        return wrapper
    return decorator
