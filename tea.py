from dataclasses import dataclass
from typing import Set


@dataclass
class Tea:
    """
    Represents a single tea in the catalog.

    Attributes
    ----------
    tea_id : str
        Unique identifier for the tea (e.g., "assam", "jasmine_pearls").
    name : str
        Human-readable name of the tea.
    kind : str
        General type of tea, e.g. "black", "green", etc.
    countries : Set[str]
        Set of country names where this tea is grown/sourced (e.g., {"China"}, {"India", "China"}).
    flavors : Set[str]
        Set of normalized flavor tags (e.g., {"floral", "smoky", "nutty"}).
    benefits : Set[str]
        Set of normalized benefit tags (e.g., {"antioxidants", "heart_health"}).
    caffeine : str
        Caffeine level, e.g. "low", "medium", "high", "very_high".
    """
    tea_id: str
    name: str
    kind: str
    countries: Set[str]
    flavors: Set[str]
    benefits: Set[str]
    caffeine: str
