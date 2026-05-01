"""Shared NFL team abbreviation normalization utilities.

The hcl game/stats tables currently store Rams as LA, while public/ESPN-facing
layers use LAR. Keep conversion logic centralized so route handlers, scripts,
and audits stay consistent.
"""

from typing import Optional


# Canonical/public format used by frontend, ESPN, and public.teams.
_TO_CANONICAL = {
    'LA': 'LAR',
    'WSH': 'WAS',
    'OAK': 'LV',
    'SD': 'LAC',
    'STL': 'LAR',
}

# Current hcl table format used for core game/stat facts.
_TO_HCL = {
    'LAR': 'LA',
    'WSH': 'WAS',
}


def _clean_abbr(abbr: Optional[str]) -> Optional[str]:
    if abbr is None:
        return None
    return abbr.strip().upper()


def to_canonical_abbr(abbr: Optional[str]) -> Optional[str]:
    """Convert any known alias to canonical/public abbreviation format."""
    clean = _clean_abbr(abbr)
    if clean is None:
        return None
    return _TO_CANONICAL.get(clean, clean)


def to_hcl_abbr(abbr: Optional[str]) -> Optional[str]:
    """Convert canonical/external abbreviation to current hcl table format."""
    clean = _clean_abbr(abbr)
    if clean is None:
        return None
    return _TO_HCL.get(clean, clean)


def sql_to_canonical_case(column_name: str) -> str:
    """Return a SQL CASE expression that normalizes a team column to canonical format."""
    return (
        f"CASE {column_name} "
        "WHEN 'LA' THEN 'LAR' "
        "WHEN 'WSH' THEN 'WAS' "
        "WHEN 'OAK' THEN 'LV' "
        "WHEN 'SD' THEN 'LAC' "
        "WHEN 'STL' THEN 'LAR' "
        f"ELSE {column_name} END"
    )
