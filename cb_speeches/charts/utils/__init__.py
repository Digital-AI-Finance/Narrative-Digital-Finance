"""
Chart utilities module for CB Speeches visualization.

This module provides shared configuration, colors, and helper functions
for creating consistent, publication-quality charts.
"""

from .style import apply_style, RCPARAMS
from .colors import COLORS, get_color, get_colorblind_palette, get_diverging_cmap, get_sequential_cmap
from .io import load_data, get_data_path, load_breakpoints
from .save import save_chart, save_to_script_dir

__all__ = [
    "apply_style",
    "RCPARAMS",
    "COLORS",
    "get_color",
    "get_colorblind_palette",
    "get_diverging_cmap",
    "get_sequential_cmap",
    "load_data",
    "get_data_path",
    "load_breakpoints",
    "save_chart",
    "save_to_script_dir",
]
