import datetime
import glob
import os
import random
import subprocess
import uuid

import pyproj
import xarray
from clover.geometry.bbox import BBox
from clover.netcdf.describe import describe
from clover.render.renderers.stretched import StretchedRenderer
from clover.render.renderers.unique import UniqueValuesRenderer
from clover.utilities.color import Color
from django.conf import settings
from django.db import Error
from ncdjango.models import Service, Variable

from landscapesim.io.query import ssim_query
from landscapesim.models import ScenarioInputServices, ScenarioOutputServices, TransitionGroup, \
    StateAttributeType, TransitionAttributeType

NC_ROOT = getattr(settings, 'NC_SERVICE_DATA_ROOT')
CLOVER_PATH = getattr(settings, 'CLOVER_PATH', None)


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
# NAME_HASH maps service name to variable named ids used by that service
NAME_HASH = {'strata': 'stratum',
             'secondary_strata': 'secondary_stratum',
             'stateclasses': 'stateclass',
             'age': 'age',
             'transition_groups': 'transition_type'}   # transition type ids are used in tg rasters

# CTYPE_HASH maps service name to raster class type
CTYPE_HASH = {'strata': 'str',
              'aatp': 'tgap',
              'stateclasses': 'sc',
              'state_attributes': 'sa',
              'transition_attributes': 'ta',
              'age': 'age',
              'transition_groups': 'tg',
              'avg_annual_transition_probability': 'tgap'}

# Sometimes we need to talk to the ssim dbs directly =)
SSIM_TABLE = {'transition_groups': 'STSim_TransitionGroup',
              'state_attributes': 'STSim_StateAttributeType',
              'transition_attributes': 'STSim_TransitionAttributeType',
              'avg_annual_transition_probability': 'STSim_TransitionGroup'}  # must match ids, since they're duplicated

# We need to match up the ssim name values to our table
INNER_TABLE = {'transition_groups': TransitionGroup,
               'state_attributes': StateAttributeType,
               'transition_attributes': TransitionAttributeType,
               'avg_annual_transition_probability': TransitionGroup}


def generate_unique_renderer(values, randomize_colors=False):
    if randomize_colors:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return UniqueValuesRenderer([(v[0], Color(r, g, b)) for v in values])
    else:
        return UniqueValuesRenderer([(v[1], Color(*[int(c) for c in v[0].split(',')[1:]])) for v in values])


def generate_stretched_renderer(info):
    v_min = None
    v_max = None
    for var in info['variables'].keys():
        if var not in ['x', 'y', 'lat', 'lon', 'latitude', 'longitude']:
            variable = info['variables'][var]
            min = variable['min']
            max = variable['max']
            v_min = min if not v_min or min < v_min else v_min
            v_max = min if not v_max or max < v_max else v_max
    v_mid = (v_max - v_min) / 2 + v_min
    return StretchedRenderer([
        (v_min, Color(240, 59, 32)),
        (v_mid, Color(254, 178, 76)),
        (v_max, Color(255, 237, 160))
    ])


def create_netcdf_dataset(scenario, nc_full_path, filename_or_pattern, variable_name, has_time):
    variable_names = []

    # No patterns, so create a simple input raster
    if not has_time:
        convert_to_netcdf(os.path.join(scenario.input_directory, filename_or_pattern), nc_full_path, variable_name)

    # Time series output pattern, convert to timeseries netcdf
    else:
        ctype = filename_or_pattern[:-4].split('-')[2:][0]
        assert ctype == CTYPE_HASH[variable_name]   # sanity check

        # collect all information to make valid patterns
        iterations = []
        timesteps = []
        ssim_ids = []

        glob_pattern = glob.glob(os.path.join(scenario.output_directory, filename_or_pattern))
        glob_pattern.sort()
        for f in glob_pattern:

            it, ts, *ctype_id = f[:-4].split(os.sep)[-1].split('-')

            if it not in iterations:
                iterations.append(it)   # E.g. ['It0001','It0002', ...]

            if ts not in timesteps:     # T.g. ['Ts0000','Ts0001', ...]
                timesteps.append(ts)

            if len(ctype_id) > 1:
                ssim_id = int(ctype_id[1])
                if ssim_id not in ssim_ids:
                    ssim_ids.append(ssim_id)    # E.g. ['tg', '93'], ['ta', '234'], etc.

            assert ctype == ctype_id[0] # pattern matching is way off (not sure this would even happen)

        # ssim_ids are internal, have to match with our system
        # service variables are <variable_name>-<inner_id>-<iteration>
        if len(ssim_ids):
            filename_patterns = []
            ssim_result = ssim_query('select * from ' + SSIM_TABLE[variable_name], scenario.project.library)

            # Create valid hash map
            ssim_hash = {}
            for id in ssim_ids:
                inner_id = None
                for row in ssim_result:
                    # match primary key id and project id, and only create filename_patterns if a match if ound
                    if id == row[0] and str(scenario.project.pid) == str(row[1]):
                        name = row[2]
                        inner_id = INNER_TABLE[variable_name].objects.filter(name__exact=name,
                                                                             project=scenario.project).first().id
                        break
                if inner_id:
                    ssim_hash[id] = inner_id

            # Now build proper filename_patterns
            for it in iterations:
                for id in ssim_ids:
                    filename_patterns.append(os.path.join(
                        scenario.output_directory, '{}-Ts*-{}-{}.tif'.format(it, ctype, id)
                    ))

            for pattern in filename_patterns:
                pattern_id = ssim_hash[int(pattern.split(os.sep)[-1].split('-')[-1][:-4])]
                iteration_num = int(pattern.split(os.sep)[-1].split('-')[0][2:])
                iteration_var_name = '{variable_name}-{id}-{iteration}'.format(
                    variable_name=variable_name,
                    id=pattern_id,
                    iteration=iteration_num
                )
                variable_names.append(iteration_var_name)
                iteration_nc_file = os.path.join(scenario.output_directory,
                                                 iteration_var_name + '.nc')
                convert_to_netcdf(pattern, iteration_nc_file, iteration_var_name)

            merge_nc_pattern = os.path.join(scenario.output_directory, variable_name + '-*-*.nc')

        # no ids
        # service variables are <variable_name>-<iteration>
        else:
            filename_patterns = [os.path.join(scenario.output_directory, '{}-Ts*-{}.tif'.format(it, ctype))
                                 for it in iterations]

            merge_nc_pattern = os.path.join(scenario.output_directory, variable_name + '-*.nc')

            for pattern in filename_patterns:
                iteration_num = int(pattern.split(os.sep)[-1].split('-')[0][2:])
                iteration_var_name = '{variable_name}-{iteration}'.format(variable_name=variable_name,
                                                                          iteration=iteration_num)
                variable_names.append(iteration_var_name)
                iteration_nc_file = os.path.join(scenario.output_directory,
                                                 iteration_var_name + '.nc')
                convert_to_netcdf(pattern, iteration_nc_file, iteration_var_name)

        merge_netcdf(merge_nc_pattern, nc_full_path)
    
    return variable_names


def generate_service(scenario, filename_or_pattern, variable_name, unique=True, has_colormap=True,
                     model_set=None, model_id_lookup=None,):
    """
    Creates an ncdjango service from a geotiff (stack).
    :param scenario:
    :param filename_or_pattern: A local filename or glob pattern.
    :param variable_name:
    :param unique:
    :param has_color: Indicate whether the service ha
    :param model_set:
    :param model_id_lookup:
    :return: One (1) ncdjango service.
    """

    has_time = '*' in filename_or_pattern   # pattern if true, filename otherwise

    # Construct relative path for new netcdf file, relative to NC_ROOT. Used as 'data_path' in ncdjango.Service
    nc_rel_path = os.path.join(scenario.project.library.name, scenario.project.name, 'Scenario-' + str(scenario.sid))
    if has_time:
        nc_rel_path = os.path.join(nc_rel_path, 'output', variable_name + '.nc')
    else:
        nc_rel_path = os.path.join(nc_rel_path, filename_or_pattern.replace('tif', 'nc'))

    # Absolute path where we want the new netcdf to live.
    nc_full_path = os.path.join(NC_ROOT, nc_rel_path)
    if not os.path.exists(os.path.dirname(nc_full_path)):
        os.makedirs(os.path.dirname(nc_full_path))

    # Create the netcdf dataset
    variable_names = create_netcdf_dataset(scenario, nc_full_path, filename_or_pattern, variable_name, has_time)

    # Now create the service
    info = describe(nc_full_path)
    grid = info['variables'][variable_names[0] if len(variable_names) else variable_name]['spatial_grid']['extent']
    extent = BBox((grid['xmin'], grid['ymin'], grid['xmax'], grid['ymax']), projection=pyproj.Proj(grid['proj4']))
    steps_per_variable = None
    t = None
    t_start = None
    t_end = None
    dimensions = list(info['dimensions'].keys())
    if 'x' in dimensions:
        x, y = ('x', 'y')
    else:
        x, y = ('lon', 'lat')
    
    if has_time:
        t = 'time'
        try:
            steps_per_variable = info['dimensions'][t]['length']
        except KeyError:
            steps_per_variable = 0
        t_start = datetime.datetime(2000, 1, 1)
        t_end = t_start + datetime.timedelta(1) * steps_per_variable

    try:
        service = Service.objects.create(
            name=uuid.uuid4(),
            data_path=nc_rel_path,
            projection=grid['proj4'],
            full_extent=extent,
            initial_extent=extent
        )

        if has_time and len(variable_names) and steps_per_variable:

            # Set required time fields
            service.supports_time = True
            service.time_start = t_start
            service.time_end = t_end
            service.time_interval = 1
            service.time_interval_units = 'days'
            service.calendar = 'standard'
            service.save()

        if unique:
            model = model_set or getattr(scenario.project, variable_name)
            unique_id_lookup = model_id_lookup or NAME_HASH[variable_name] + '_id'
            try:
                if has_colormap:
                    queryset = model.values_list('color', unique_id_lookup)
                    renderer = generate_unique_renderer(queryset)
                else:
                    queryset = model.values_list(unique_id_lookup)
                    renderer = generate_unique_renderer(queryset, randomize_colors=True)
            except:
                raise AssertionError(CREATE_RENDERER_ERROR_MSG.format(vname=variable_name))
        else:
            renderer = generate_stretched_renderer(info)

        if has_time and len(variable_names):

            for name in variable_names:
                Variable.objects.create(
                    service=service,
                    index=variable_names.index(name),
                    variable=name,
                    projection=grid['proj4'],
                    x_dimension=x,
                    y_dimension=y,
                    name=name,
                    renderer=renderer,
                    full_extent=extent,
                    supports_time=True,
                    time_dimension=t,
                    time_start=t_start,
                    time_end=t_end,
                    time_steps=steps_per_variable
                )

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


# TODO - allow us to update a service with a given service and the path to the tif data to be added onto it
# From there, we want to signal to the user that this service has been updated with the latest timestep to visualize.
def update_service(*args, **kwargs):
    #scan_directory = scenario.output_directory
    #tifs = glob.glob(os.path.join(scenario.output_directory, ))
    pass


def convert_to_netcdf(geotiff_file_or_pattern, netcdf_out, variable_name):
    """
    Convert input rasters to netcdf for use in ncdjango
    :param geotiff_in: Absolute path to geotiff to convert
    :param netcdf_out: Absolute path to netCDF file
    :param variable_name: The variable name
    """

    try:
        subprocess.run([CLOVER_PATH if CLOVER_PATH else "clover", "to_netcdf", geotiff_file_or_pattern, netcdf_out, variable_name])
    except:
        raise subprocess.SubprocessError("Failed calling clover. Did you setup clover correctly?")


def merge_netcdf(pattern, out):
    """
    Merges a list of netcdf files with different variables and same dimensions into a single netcdf file.
    :param pattern: glob.glob pattern (not necessarily a regex)
    """
    glob_pattern = glob.glob(pattern)
    glob_pattern.sort()
    xarray.merge(xarray.open_dataset(x) for x in glob_pattern).to_netcdf(out)


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
        sis.secondary_stratum = generate_service(scenario, ics.secondary_stratum_file_name,
                                                 'secondary_strata', has_colormap=False)

    if len(ics.stateclass_file_name):
        sis.stateclass = generate_service(scenario, ics.stateclass_file_name, 'stateclasses')

    if len(ics.age_file_name):
        sis.age = generate_service(scenario, ics.age_file_name, 'age', unique=False)

    sis.save()


@has_nc_root
def process_output_rasters(scenario):
    """
    Generates a set of ncdjango services and time-series variables to associate with a scenario.
    :param scenario: A result scenario containing output rasters.
    """

    assert scenario.is_result   # sanity check

    sos, _ = ScenarioOutputServices.objects.get_or_create(scenario=scenario)
    oo = scenario.output_options

    if oo.raster_sc:
        sos.stateclass = generate_service(scenario, 'It*-Ts*-sc.tif', 'stateclasses')

    if oo.raster_tr:
        sos.transition_group = generate_service(scenario, 'It*-Ts*-tg-*.tif', 'transition_groups',
                                                has_colormap=False, model_set=scenario.project.transition_types,
                                                model_id_lookup='transition_type_id')

    if oo.raster_sa:
        sos.state_attribute = generate_service(scenario, 'It*-Ts*-sa-*.tif', 'state_attributes', unique=False)

    if oo.raster_ta:
        sos.transition_attribute = generate_service(scenario, 'It*-Ts*-ta-*.tif', 'transition_attributes', unique=False)

    if oo.raster_strata:
        sos.stratum = generate_service(scenario, 'It*-Ts*-str.tif', 'strata')

    if oo.raster_age:
        sos.age = generate_service(scenario, 'It*-Ts*-age.tif', 'age', unique=False)

    if oo.raster_tst:
        # TODO - implement RasterOutputTST (find use case first)
        print("RasterOutputTST not implemented yet. For now, please disable this output option.")

    if oo.raster_aatp:
        sos.avg_annual_transition_group_probability = generate_service(scenario, 'It*-Ts*-tgap-*.tif',
                                                                       'avg_annual_transition_probability',
                                                                       unique=False)

    sos.save()
