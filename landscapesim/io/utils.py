from uuid import uuid4

M2_TO_ACRES = 0.000247105


# meters squared to acres
def cells_to_acres(numcells, res):
    return pow(res, 2) * M2_TO_ACRES * numcells


# Get a random CSV based of a template file path for another CSV file
def get_random_csv(file):
    return file.replace('.csv', str(uuid4()) + '.csv')


# Convert a color string into it's component parts
def color_to_rgba(colorstr):
    r, g, b, a = colorstr.split(',')
    return {'r': r, 'g': g, 'b': b, 'a': a}

