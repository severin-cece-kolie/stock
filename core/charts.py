"""
Génération de graphiques SVG côté serveur, dans le style exact de la
maquette Stitch (dégradé sous la courbe, points de données, grille).
Utilisé par le module Reports ET le Dashboard, pour rester fidèle au
design sans dépendre d'une librairie JS externe (Chart.js).
"""


def line_chart_svg(values, gradient_id='chartGradient', stroke='#2170e4', fill='#0058be'):
    """
    values : liste de nombres (>= 2 éléments).
    Retourne un dict avec le path de la courbe, le path du remplissage
    dégradé, et les points, tous en coordonnées 0-100 (viewBox 0 0 100 100)
    — exactement comme dans le Stitch original.
    """
    if not values:
        values = [0]
    if len(values) == 1:
        values = values * 2

    vmin, vmax = min(values), max(values)
    span = (vmax - vmin) or 1
    n = len(values)

    points = []
    for i, v in enumerate(values):
        x = (i / (n - 1)) * 100 if n > 1 else 0
        # inversé : forte valeur -> y petit (proche du haut du SVG)
        y = 100 - ((v - vmin) / span) * 90 - 5
        points.append((round(x, 2), round(y, 2)))

    line_path = 'M' + ' L'.join(f"{x},{y}" for x, y in points)
    fill_path = line_path + f" L100,100 L0,100 Z"

    return {
        'line_path': line_path,
        'fill_path': fill_path,
        'points': points,
        'gradient_id': gradient_id,
        'stroke': stroke,
        'fill': fill,
        'max_value': vmax,
        'min_value': vmin,
    }


def bar_heights_percent(values):
    """Retourne les hauteurs en % (0-100) pour un bar chart CSS, comme dans le Stitch."""
    if not values:
        return []
    vmax = max(values) or 1
    return [round((v / vmax) * 100, 1) if vmax else 0 for v in values]
