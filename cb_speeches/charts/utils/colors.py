"""
Colorblind-safe color palette for CB Speeches charts.

Uses the Okabe-Ito palette, which is designed to be distinguishable
by people with various forms of color vision deficiency.

Reference: https://jfly.uni-koeln.de/color/
"""

from typing import List, Dict

# Okabe-Ito colorblind-safe palette
# These colors are distinguishable by people with color vision deficiency
OKABE_ITO: Dict[str, str] = {
    'orange': '#E69F00',
    'sky_blue': '#56B4E9',
    'green': '#009E73',
    'yellow': '#F0E442',
    'blue': '#0072B2',
    'vermillion': '#D55E00',
    'purple': '#CC79A7',
    'black': '#000000',
}

# Semantic color mappings for CB Speeches analysis
COLORS: Dict[str, str] = {
    # Primary colors for main data
    'primary': OKABE_ITO['blue'],
    'secondary': OKABE_ITO['vermillion'],
    'tertiary': OKABE_ITO['green'],

    # Sentiment colors
    'hawkish': OKABE_ITO['vermillion'],
    'dovish': OKABE_ITO['blue'],
    'neutral': OKABE_ITO['black'],

    # Macro/economic colors
    'macro': OKABE_ITO['blue'],
    'inflation': OKABE_ITO['vermillion'],
    'policy': OKABE_ITO['green'],

    # Chart element colors
    'line': OKABE_ITO['blue'],
    'fill': OKABE_ITO['sky_blue'],
    'highlight': OKABE_ITO['orange'],
    'breakpoint': OKABE_ITO['vermillion'],
    'regime': OKABE_ITO['sky_blue'],

    # Positive/negative
    'positive': OKABE_ITO['green'],
    'negative': OKABE_ITO['vermillion'],

    # Gray scale
    'gray_dark': '#333333',
    'gray_medium': '#666666',
    'gray_light': '#999999',
    'gray_very_light': '#cccccc',

    # Background
    'background': '#ffffff',
    'grid': '#e0e0e0',

    # Source attribution
    'source_text': '#666666',
}


def get_color(name: str) -> str:
    """
    Get a color by semantic name.

    Parameters
    ----------
    name : str
        Semantic color name (e.g., 'hawkish', 'macro', 'primary')

    Returns
    -------
    str
        Hex color code

    Raises
    ------
    KeyError
        If color name is not found
    """
    if name not in COLORS:
        raise KeyError(f"Unknown color: '{name}'. Available: {list(COLORS.keys())}")
    return COLORS[name]


def get_colorblind_palette(n: int = 8) -> List[str]:
    """
    Get a list of n colorblind-safe colors.

    Parameters
    ----------
    n : int
        Number of colors needed (max 8)

    Returns
    -------
    List[str]
        List of hex color codes

    Raises
    ------
    ValueError
        If n > 8
    """
    if n > 8:
        raise ValueError(f"Maximum 8 colors available, requested {n}")

    palette = list(OKABE_ITO.values())
    return palette[:n]


def get_sequential_cmap() -> str:
    """
    Get the recommended sequential colormap name.

    Returns 'YlOrRd' which works well for sequential data and
    is reasonably accessible.

    Returns
    -------
    str
        Matplotlib colormap name
    """
    return 'YlOrRd'


def get_diverging_cmap() -> str:
    """
    Get the recommended diverging colormap name.

    Returns 'RdBu_r' which is a good diverging colormap
    for correlation matrices and similar.

    Returns
    -------
    str
        Matplotlib colormap name
    """
    return 'RdBu_r'
