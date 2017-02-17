
# Utils for simple conversions


def color_to_rgba(colorstr):
    r, g, b, a = colorstr.split(',')
    return {'r': r, 'g': g, 'b': b, 'a': a}

