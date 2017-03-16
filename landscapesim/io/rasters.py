import os
import random
import subprocess
import glob
import pyproj
import xarray
from clover.geometry.bbox import BBox
from clover.netcdf.describe import describe
from clover.render.renderers.unique import UniqueValuesRenderer
from clover.utilities.color import Color
from django.conf import settings
from django.db import Error
from ncdjango.models import Service, Variable
from landscapesim.io.query import ssim_query
from landscapesim.models import ScenarioInputServices, ScenarioOutputServices, TransitionGroup, \
    StateAttributeType, TransitionAttributeType

NC_ROOT = getattr(settings, 'NC_SERVICE_DATA_ROOT')


# Sanity check for creating ncdjango services correctly
def has_nc_root(func):
    def wrapper(*args, **kwargs):
        if NC_ROOT:
            return func(*args, **kwargs)
        else:
            print('NC_SERVICE_DATA_ROOT not set. Did you install and setup ncdjango properly?')
    return wrapper


CREATE_SERVICE_ERROR_MSG = "Error creating ncdjango service for {} in scenario {}, skipping..."
CREATE_RENDERER_ERROR_MSG = "Error creating renderer for {vname}. Did you set ID values for your {vname} definitions?"

# Some variables don't quite line up, but this is by design.
# NAME_HASH maps service name to variable named ids
NAME_HASH = {'strata': 'stratum',
             'secondary_strata': 'secondary_stratum',
             'stateclasses': 'stateclass',
             'age': 'age'}

# CTYPE_HASH maps service name to raster class type
CTYPE_HASH = {'strata': 'str',
              'aatp': 'tgap',
              'stateclasses': 'sc',
              'state_attributes': 'sa',
              'transition_attributes': 'ta',
              'transition_groups': 'tg'}

# Sometimes we need to talk to the ssim dbs directly =)
SSIM_TABLE = {'transition_groups': 'STSim_TransitionGroup',
              'state_attributes': 'STSim_StateAttributeType',
              'transition_attributes': 'STSim_TransitionAttributeType'}

# We need to match up the ssim name values to our table
INNER_TABLE = {'transition_groups': TransitionGroup,
               'state_attributes': StateAttributeType,
               'transition_attributes': TransitionAttributeType}

def generate_unique_renderer(values, randomize_colors=False):
    if randomize_colors:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return UniqueValuesRenderer([(v[0], Color(r, g, b)) for v in values])
    else:
        return UniqueValuesRenderer([(v[1], Color(*[int(c) for c in v[0].split(',')[1:]])) for v in values])


def generate_stretched_renderer(info):

    raise NotImplementedError("Stretched renderer not implemented (yet).")


def generate_service_name(scenario, variable_name, is_output=False):
    return "lib-{}-proj-{}-scenario-{}/{}".format(
        scenario.project.library_id, scenario.project_id, scenario.id,
        variable_name + '-output' if is_output else variable_name
    )


def generate_service(scenario, filename_or_pattern, variable_name, unique=True, has_color=True, has_time=False):
    """
    Creates an ncdjango service from a geotiff (stack).
    :param scenario:
    :param filename_or_pattern: A local filename or glob pattern.
    :param variable_name:
    :param unique:
    :param has_color:
    :param has_time:
    :return:
    """

    # Construct relative path for new netcdf file, relative to NC_ROOT
    nc_rel_path = os.path.join(scenario.project.library.name, scenario.project.name, 'Scenario-' + str(scenario.sid))
    if has_time:
        nc_rel_path = os.path.join(nc_rel_path, 'output', variable_name + '.nc')
    else:
        if '*' in filename_or_pattern:
            raise ValueError("Supplied a pattern with no time-enabled component.")

        nc_rel_path = os.path.join(nc_rel_path, filename_or_pattern.replace('tif', 'nc'))

    # Absolute path where we want the new netcdf to live.
    nc_full_path = os.path.join(NC_ROOT, nc_rel_path)
    if not os.path.exists(os.path.dirname(nc_full_path)):
        os.makedirs(os.path.dirname(nc_full_path))

    ctype = None
    variable_names = []

    # Time series output pattern, convert to timeseries netcdf
    if '*' in filename_or_pattern:

        ctype = filename_or_pattern.split('-')[2:][0]

        assert ctype == CTYPE_HASH[variable_name]   # sanity check

        # collect all information to make valid patterns
        iterations = []
        timesteps = []
        ssim_ids = []
        for f in glob.glob(os.path.join(scenario.output_directory(), filename_or_pattern)):

            it, _, *ctype_id = f[:-4].split(os.sep)[-1].split('-')

            if it not in iterations:
                iterations.append(it)   # E.g. ['It0001','It0002', ...]

            if _ not in timesteps:     # T.g. ['Ts0000','Ts0001', ...]
                timesteps.append(_)

            if len(ctype_id) > 1:
                ssim_ids.append(int(ctype_id[1]))    # E.g. ['tg', '93'], ['ta', '234'], etc.

            assert ctype == ctype_id[0] # pattern matching is way off (not sure this would even happen)

        # ssim_ids are internal, have to match with our system
        # service variables are <variable_name>-<inner_id>-<iteration>
        if len(ssim_ids):
            filename_patterns = []
            ssim_result = ssim_query('select * from ' + SSIM_TABLE[variable_name], scenario.project.library)
            for id in ssim_ids:
                id_patterns = []
                for it in iterations:
                    inner_id = None
                    for row in ssim_result:
                        if id == row[0] and str(scenario.project.pid) == str(row[1]): # matches primary key id and project id
                            name = row[2]
                            inner_id = INNER_TABLE[variable_name].objects\
                                .filter(name__exact=name, project=scenario.project).first()\
                                .id

                    if inner_id:
                        id_patterns.append(os.path.join(scenario.output_directory(),
                                                              it + '-Ts*-' + ctype + '-' + id + '.tif'))
                filename_patterns.append(id_patterns)

            for pattern_list in filename_patterns:
                pattern_id = int(pattern_list[0].split(os.sep)[-1].split('-')[-1][:-4])
                for pattern in pattern_list:
                    iteration_num = int(pattern.split(os.sep)[-1].split('-')[0][2:])
                    iteration_var_name = variable_name + '-' + str(pattern_id) + '-' + str(iteration_num)
                    variable_names.append(iteration_var_name)
                    iteration_nc_file = os.path.join(scenario.output_directory(),
                                                     iteration_var_name + '.nc')
                    convert_to_netcdf(pattern, iteration_nc_file, iteration_var_name)

            merged_nc_pattern = os.path.join(scenario.output_directory(), variable_name + '-*-*.nc')

        # no ids
        # service variables are <variable_name>-<iteration>
        else:
            filename_patterns = [os.path.join(scenario.output_directory(),
                                              it + '-Ts*-' + ctype + '.tif')
                                 for it in iterations]

            merged_nc_pattern = os.path.join(scenario.output_directory(), variable_name + '-*.nc')

            for pattern in filename_patterns:
                iteration_num = int(pattern.split(os.sep)[-1].split('-')[0][2:])
                iteration_var_name = variable_name + '-' + str(iteration_num)
                variable_names.append(iteration_var_name)
                iteration_nc_file = os.path.join(scenario.output_directory(),
                                                 iteration_var_name + '.nc')
                convert_to_netcdf(pattern, iteration_nc_file, iteration_var_name)

        merge_netcdf(merged_nc_pattern, nc_full_path)

    # No patterns, so create a simple input raster
    else:
        convert_to_netcdf(os.path.join(scenario.input_directory(), filename_or_pattern), nc_full_path, variable_name)

    info = describe(nc_full_path)
    grid = info['variables'][variable_name]['spatial_grid']['extent']
    extent = BBox((grid['xmin'], grid['ymin'], grid['xmax'], grid['ymax']), projection=pyproj.Proj(grid['proj4']))
    y, x = list(info['dimensions'].keys())

    try:
        # Create the name of the ncdjango service.
        service_name = generate_service_name(scenario, variable_name, is_output=has_time)

        service = Service.objects.create(
            name=service_name,
            data_path=nc_rel_path,
            projection=grid['proj4'],
            full_extent=extent,
            initial_extent=extent
        )

        if has_time and len(variable_names):

            # something something time stuff

            service.save()

            pass # TODO - Add info for handling services that are timeseries


        if unique:
            try:
                if has_color:
                    queryset = getattr(scenario.project, variable_name).values_list('color', NAME_HASH[variable_name] + '_id')
                    renderer = generate_unique_renderer(queryset)
                else:
                    queryset = getattr(scenario.project, variable_name).values_list(NAME_HASH[variable_name] + '_id')
                    renderer = generate_unique_renderer(queryset, randomize_colors=True)
            except:
                raise AssertionError(CREATE_RENDERER_ERROR_MSG.format(vname=variable_name))
        else:
            renderer = generate_stretched_renderer(info)

        if has_time and len(variable_names):
            pass    # TODO - handle creating variables that handle time
        else:
            Variable.objects.create(
                service=service,
                index=0,
                variable=variable_name,
                projection=grid['proj4'],
                x_dimension=x,
                y_dimension=y,
                name=variable_name,
                renderer=renderer,
                full_extent=extent
            )

        return service

    except:
        raise Error(CREATE_SERVICE_ERROR_MSG.format(variable_name, scenario.sid))


def convert_to_netcdf(geotiff_file_or_pattern, netcdf_out, variable_name):
    """
    Convert input rasters to netcdf for use in ncdjango
    :param geotiff_in: Absolute path to geotiff to convert
    :param netcdf_out: Absolute path to netCDF file
    :param variable_name: The variable name
    """

    try:
        subprocess.run(["clover", "to_netcdf", geotiff_file_or_pattern, netcdf_out, variable_name])
    except:
        raise subprocess.CalledProcessError("Failed calling clover. Did you setup clover correctly?")


def merge_netcdf(pattern, out):
    """
    Merges a list of netcdf files with different variables and same dimensions into a single netcdf file.
    :param pattern: glob.glob pattern (not necessarily a regex)
    """
    xarray.merge([xarray.open_dataset(x) for x in glob.glob(pattern)]).to_netcdf(out)


@has_nc_root
def process_input_rasters(ics):
    """
    Generates a set of ncdjango services and variables (1 to 1) to associate with a scenario.
    :param ics: InitialConditionsSpatial model instance
    :return: None
    """

    scenario = ics.scenario
    sis = ScenarioInputServices.objects.create(scenario=ics.scenario)

    # Create stratum input service
    if len(ics.stratum_file_name):
        sis.stratum = generate_service(scenario, ics.stratum_file_name, 'strata')

    if len(ics.secondary_stratum_file_name):
        sis.secondary_stratum = generate_service(scenario, ics.secondary_stratum_file_name, 'secondary_strata', has_color=False)

    if len(ics.stateclass_file_name):
        sis.stateclass = generate_service(scenario, ics.stateclass_file_name, 'stateclasses')

    if len(ics.age_file_name):
        sis.age = generate_service(scenario, ics.age_file_name, 'age', unique=False)

    sis.save()


@has_nc_root
def process_output_rasters(scenario):
    """
    Generates a set of ncdjango services and time-series variables to associate with a scenario.
    :param scenario: A result scenario.
    """

    assert scenario.is_result   # sanity check

    sos = ScenarioOutputServices.objects.create(scenario=scenario)
    oo = scenario.output_options

    if oo.raster_sc:
        sos.stateclass = generate_service(scenario, 'It*-Ts*-sc.tif', 'stateclasses')  # ctype = sc

    if oo.raster_tr:
        pass

    if oo.raster_sa:
        pass

    if oo.raster_ta:
        pass

    if oo.raster_strata:
        pass

    if oo.raster_age:
        pass

    if oo.raster_tst:
        pass

    #if oo.raster_aatp: # TODO - this is handled weirdly, only outputting 0th iteration and 0th timestep
    #    pass
