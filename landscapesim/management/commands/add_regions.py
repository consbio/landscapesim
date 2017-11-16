""" TODO - create ReportingUnits that can be used in any library. """

"""

The goal is to create a script that simply imports the necessary reporting unit data,
and associates it with a frontend such that any frontend can use the reporint unit.

The reason for
having a table as opposed to just a simple geojson file is because we will want to use the ID of the
reporting unit to link that reporting unit to a raster creation process for initial conditions. This was,
we can both query a library's large spatial extent for initial conditions for a specific area. This is
better handled by a database than the frontend user code.

"""