"""
Canonical matplotlib style for Mobile Monster analytics charts.

Usage:
    import sys; sys.path.insert(0, '.claude/skills/shopify-analytics')
    from chart_style import apply_style, PALETTE, kpi_header, money_fmt, kilo_fmt
    apply_style()
    fig = plt.figure(figsize=(15, 9), facecolor='white')
    kpi_header(fig, title='OzMobiles - Sales Report',
               subtitle='Last 7 days - Melbourne (AEST)',
               kpis=[('Revenue', '$182,532', PALETTE['primary']),
                     ('Orders',  '246',      PALETTE['text']),
                     ('AOV',     '$742',     PALETTE['accent']),
                     ('Refunds', '$636',     PALETTE['secondary'])])
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PALETTE = {
    'primary':   '#2563eb',
    'secondary': '#ef4444',
    'accent':    '#10b981',
    'warning':   '#f59e0b',
    'muted':     '#9ca3af',
    'text':      '#111827',
    'subtext':   '#6b7280',
    'grid':      '#f3f4f6',
    'spine':     '#e5e7eb',
}

SERIES_COLORS = [PALETTE['primary'], PALETTE['accent'], PALETTE['warning'],
                 PALETTE['secondary'], PALETTE['muted'], '#8b5cf6', '#06b6d4']


def apply_style():
    """Apply the canonical rcParams. Call once before creating figures."""
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'axes.edgecolor': PALETTE['spine'],
        'axes.linewidth': 1.0,
        'axes.labelcolor': '#374151',
        'axes.titleweight': 'bold',
        'axes.titlesize': 13,
        'axes.titlecolor': PALETTE['text'],
        'xtick.color': PALETTE['subtext'],
        'ytick.color': PALETTE['subtext'],
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'axes.grid': True,
        'grid.color': PALETTE['grid'],
        'grid.linewidth': 0.8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.prop_cycle': plt.cycler(color=SERIES_COLORS),
        'figure.facecolor': 'white',
        'savefig.facecolor': 'white',
        'savefig.dpi': 170,
        'savefig.bbox': 'tight',
    })


def money_fmt(decimals: int = 0):
    """Axis formatter for dollar amounts: $1,234."""
    return mticker.FuncFormatter(lambda x, _: f'${x:,.{decimals}f}')


def kilo_fmt():
    """Axis formatter for $k thousands: $120k."""
    return mticker.FuncFormatter(lambda x, _: f'${x/1000:,.0f}k')


def kpi_header(fig, *, title: str, subtitle: str, kpis: list[tuple[str, str, str]],
               top: float = 0.93):
    """
    Render a title + subtitle + KPI strip at the top of a figure.

    Args:
        fig: matplotlib Figure
        title: main title (e.g. "OzMobiles - Sales Report")
        subtitle: period + timezone line
        kpis: list of (label, value, color) tuples (up to 6)
        top: y-position (figure coords) for the top of the header area
    """
    ax = fig.add_axes([0.07, top - 0.12, 0.89, 0.12])
    ax.axis('off')
    ax.text(0.0, 0.85, title, fontsize=20, fontweight='bold',
            color=PALETTE['text'], transform=ax.transAxes)
    ax.text(0.0, 0.45, subtitle, fontsize=11,
            color=PALETTE['subtext'], transform=ax.transAxes)
    n = len(kpis)
    if n == 0:
        return ax
    # right-align KPI block starting ~35% of width
    total_w = 0.65
    step = total_w / n
    for i, (label, val, col) in enumerate(kpis):
        x = 0.35 + i * step
        ax.text(x, 0.80, val, fontsize=18, fontweight='bold',
                color=col, transform=ax.transAxes)
        ax.text(x, 0.35, label.upper(), fontsize=9, fontweight='bold',
                color=PALETTE['subtext'], transform=ax.transAxes)
    return ax


def label_bars(ax, bars, values, *, fmt='${:,.0f}', pad_pct: float = 0.02,
               color: str = None):
    """Put a value label on top of each bar."""
    col = color or PALETTE['text']
    ymax = max(values) if values else 0
    pad = ymax * pad_pct
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + pad, fmt.format(v),
                ha='center', va='bottom', fontsize=10,
                fontweight='bold', color=col)


def footer(fig, text: str):
    """Italic grey footer line at the very bottom."""
    fig.text(0.5, 0.015, text, ha='center', fontsize=8,
             color=PALETTE['muted'], style='italic')


def change_badge(value: float, *, pct: bool = True) -> tuple[str, str]:
    """Return (text, color) for an up/down change indicator.

    Never relies on color alone - always emits an up/down arrow for color-blind safety.
    """
    if value > 0:
        return (f"^ +{value:.1f}%" if pct else f"^ +{value:,.0f}", PALETTE['accent'])
    if value < 0:
        return (f"v {value:.1f}%" if pct else f"v {value:,.0f}", PALETTE['secondary'])
    return ("- 0%" if pct else "- 0", PALETTE['muted'])
