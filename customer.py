from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set
from collections import Counter

from tea import Tea


@dataclass
class Customer:
    """
    Represents a customer interacting with the tea recommendation system.

    The class aggregates preference signals from:
    - Survey answers (explicit preferences)
    - Views of teas
    - Purchases of teas

    All of these signals update internal preference counters over:
    - tea kinds
    - countries of origin
    - flavors
    - benefits
    - caffeine levels
    """

    customer_id: str
    name: str | None = None

    # ---------- implicit behavior-based data ----------

    # How many times each tea was purchased / viewed
    purchased_teas: Counter = field(default_factory=Counter)   # tea_id -> count
    viewed_teas: Counter = field(default_factory=Counter)      # tea_id -> count

    # Aggregated preference counters over tea attributes
    kind_preferences: Counter = field(default_factory=Counter)      # kind -> score
    country_preferences: Counter = field(default_factory=Counter)   # country -> score
    flavor_preferences: Counter = field(default_factory=Counter)    # flavor -> score
    benefit_preferences: Counter = field(default_factory=Counter)   # benefit -> score
    caffeine_preferences: Counter = field(default_factory=Counter)  # caffeine level -> score

    # ---------- explicit survey answers (optional to keep) ----------

    # None or empty set == "no preference" for that category
    preferred_kinds: Set[str] | None = None
    preferred_countries: Set[str] | None = None
    preferred_flavors: Set[str] | None = None
    preferred_benefits: Set[str] | None = None
    preferred_caffeine: Set[str] | None = None

    # ---------- weights for different signals (tunable) ----------

    # how strongly each interaction influences preferences
    VIEW_WEIGHT: int = 1       # per view
    PURCHASE_WEIGHT: int = 5   # per purchase
    SURVEY_WEIGHT: int = 10    # per survey choice

    # ---------- internal helpers ----------

    def _apply_attribute_weights(self, tea: Tea, weight: int) -> None:
        """
        Internal helper: apply the given weight to all attribute preference
        counters based on the attributes of a given tea.
        """
        # kind
        self.kind_preferences[tea.kind] += weight

        # countries
        for country in tea.countries:
            self.country_preferences[country] += weight

        # flavors
        for flavor in tea.flavors:
            self.flavor_preferences[flavor] += weight

        # benefits
        for benefit in tea.benefits:
            self.benefit_preferences[benefit] += weight

        # caffeine
        self.caffeine_preferences[tea.caffeine] += weight

    # ---------- interaction methods (views & purchases) ----------

    def add_view(self, tea: Tea, times: int = 1) -> None:
        """
        Record that the customer viewed a tea.

        Each view contributes VIEW_WEIGHT to all of the tea's attributes
        (kind, countries, flavors, benefits, caffeine).
        """
        if times <= 0:
            return

        self.viewed_teas[tea.tea_id] += times
        total_weight = self.VIEW_WEIGHT * times
        self._apply_attribute_weights(tea, total_weight)

    def add_purchase(self, tea: Tea, times: int = 1) -> None:
        """
        Record that the customer purchased a tea.

        Each purchase contributes PURCHASE_WEIGHT to all of the tea's attributes.
        """
        if times <= 0:
            return

        self.purchased_teas[tea.tea_id] += times
        total_weight = self.PURCHASE_WEIGHT * times
        self._apply_attribute_weights(tea, total_weight)

    # ---------- survey / explicit preference API ----------

    def set_survey_preferences(
        self,
        kinds: List[str] | None = None,
        countries: List[str] | None = None,
        flavors: List[str] | None = None,
        benefits: List[str] | None = None,
        caffeine_levels: List[str] | None = None,
    ) -> None:
        """
        Initialize or overwrite explicit preferences from an initial survey.

        Passing None or an empty list for a parameter means "no preference"
        for that category.

        Each selected value contributes SURVEY_WEIGHT to the corresponding
        preference counter, making survey answers the strongest signal.
        """
        # Store explicit selections (for explanation or debugging)
        self.preferred_kinds = set(kinds) if kinds else None
        self.preferred_countries = set(countries) if countries else None
        self.preferred_flavors = set(flavors) if flavors else None
        self.preferred_benefits = set(benefits) if benefits else None
        self.preferred_caffeine = set(caffeine_levels) if caffeine_levels else None

        w = self.SURVEY_WEIGHT

        if kinds:
            for k in kinds:
                self.kind_preferences[k] += w

        if countries:
            for c in countries:
                self.country_preferences[c] += w

        if flavors:
            for f in flavors:
                self.flavor_preferences[f] += w

        if benefits:
            for b in benefits:
                self.benefit_preferences[b] += w

        if caffeine_levels:
            for caff in caffeine_levels:
                self.caffeine_preferences[caff] += w

    # ---------- helper flags for "no preference" ----------

    def has_kind_preference(self) -> bool:
        return bool(self.preferred_kinds)

    def has_country_preference(self) -> bool:
        return bool(self.preferred_countries)

    def has_flavor_preference(self) -> bool:
        return bool(self.preferred_flavors)

    def has_benefit_preference(self) -> bool:
        return bool(self.preferred_benefits)

    def has_caffeine_preference(self) -> bool:
        return bool(self.preferred_caffeine)

    # ---------- convenience accessors ----------

    @property
    def purchased_ids(self) -> Set[str]:
        """Set of tea_ids the customer has ever purchased."""
        return set(self.purchased_teas.keys())

    @property
    def viewed_ids(self) -> Set[str]:
        """Set of tea_ids the customer has ever viewed."""
        return set(self.viewed_teas.keys())

    # ---------- inspection utilities (useful for debugging / report) ----------

    def top_flavors(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the top-n flavors by aggregated preference score."""
        return self.flavor_preferences.most_common(n)

    def top_benefits(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the top-n benefits by aggregated preference score."""
        return self.benefit_preferences.most_common(n)

    def top_kinds(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the top-n tea kinds by preference score."""
        return self.kind_preferences.most_common(n)

    def top_countries(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the top-n countries of origin by preference score."""
        return self.country_preferences.most_common(n)

    def top_caffeine_levels(self, n: int = 5) -> List[Tuple[str, int]]:
        """Return the top-n caffeine levels by preference score."""
        return self.caffeine_preferences.most_common(n)

    def recommend_teas(self, teas: list[Tea], top_n: int = 5) -> list[tuple[Tea, int]]:
        scored = []
        for tea in teas:
            score = 0
            score += self.kind_preferences.get(tea.kind, 0)
            score += self.caffeine_preferences.get(tea.caffeine, 0)
            score += sum(self.country_preferences.get(c, 0) for c in tea.countries)
            score += sum(self.flavor_preferences.get(f, 0) for f in tea.flavors)
            score += sum(self.benefit_preferences.get(b, 0) for b in tea.benefits)
            scored.append((tea, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

