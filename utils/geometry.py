def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    p1x, p1y = polygon[0]

    for i in range(len(polygon) + 1):
        p2x, p2y = polygon[i % len(polygon)]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y

    return inside
