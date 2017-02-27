"""
SyncroSim Command-Line Wrapper. Provides tools for interacting programmatically with SyncroSim consoles.

Available Consoles (Verbose Name, basename, Python class):
    - System Console                        'system'        Console
    - ST-Sim State and Transition Console   'stsim'         STSimConsole
    - Stocks and Flows Console              'stockflow'     StockFlowConsole

"""

import subprocess
import os
import csv
import rasterio
from collections import OrderedDict
from django_stsim.io.utils import M2_TO_ACRES, order

# The standard installation location for SyncroSim (subject to change, also not valid for linux...)
DEFAULT_EXE = "C:\\Program Files\\SyncroSim\\1\\SyncroSim.Console.Exe"


class ConsoleMeta(type):
    """  Metaclass for handling the different console names, enforcing each console to specify a name """
    def __init__(cls, name, bases, attrs):
        if 'name' not in attrs:
            raise ValueError("Class {name} doesn't define a console name.".format(name=name))
        type.__init__(cls, name, bases, attrs)


class Console:
    """ System Console class. Provides lots of basic I/O functions for running models and working with sheets."""

    __metaclass__ = ConsoleMeta

    name = 'system'  # name is never needed for the system console, but subclasses require this to be known

    def __init__(self, **kwargs):
        if 'lib_path' not in kwargs:
            raise ValueError("Invalid input params. Make sure to specify 'lib_path'")
        self.prefix = 'mono' if os.name == 'posix' else ''
        self.sep = '\r\n' if os.name != 'posix' else '\n'
        exe = os.path.abspath((DEFAULT_EXE if 'exe' not in kwargs else kwargs['exe']))
        self.lib = os.path.abspath(kwargs['lib_path'])
        self.exe_lib = [exe, "--lib=" + self.lib]

        # test working executable
        try:
            self.exec_command(["--version"])
        except FileNotFoundError:
            if exe == DEFAULT_EXE:
                raise ValueError("The path to the default installation is not valid (" + DEFAULT_EXE + "), or the path"+
                                 " provided for the exe was invalid")
            else:
                raise ValueError("The provided executable path for SyncroSim is invalid.\nProvided path was: " + exe)

        # test working library paths and create spatial directories for each library as needed
        try:
            self.list_datafeeds()
            self.spatial_input_dir = self.lib + '.input'
            self.spatial_output_dir = self.lib + '.output'
            if not os.path.exists(self.spatial_input_dir):
                os.mkdir(self.spatial_input_dir)
            if not os.path.exists(self.spatial_output_dir):
                os.mkdir(self.spatial_output_dir)
        except:
            raise ValueError("The provided library path is invalid.\nProvided path was: " + self.lib)

        self.exe_orig_lib = None
        if 'orig_lib_path' in kwargs:
            self.orig_lib = os.path.abspath(kwargs['orig_lib_path'])
            self.exe_orig_lib = [exe, "--lib=" + self.orig_lib]
            try:
                self.list_datafeeds(orig=True)
                self.spatial_orig_input_dir = self.orig_lib + '.input'
                self.spatial_orig_output_dir = self.orig_lib + '.output'
                if not os.path.exists(self.spatial_orig_input_dir):
                    os.mkdir(self.spatial_orig_input_dir)

                # TODO - verify that all the scenario IDs in the original library exist in the working library

            except:
                raise ValueError("The provided library path is invalid.\nProvided path was: " + self.orig_lib)

        # verify that all the necessary directories exist for all the existing scenarios
        self.verify_spatial_directories()

    def __str__(self):

        return self.lib

    def verify_spatial_directories(self):

        scenarios = self.list_scenarios()
        result_scenarios = self.list_scenarios(results_only=True)
        if self.exe_orig_lib is not None:
            orig_scenarios = self.list_scenarios(orig=True)
        else:
            orig_scenarios = None

        for sid in scenarios:
            scenario_dir = os.path.join('Scenario-' + str(sid), 'STSim_InitialConditionsSpatial')
            # create input directories for every scenario
            input_path = os.path.join(self.spatial_input_dir, scenario_dir)
            if not os.path.exists(input_path):
                os.makedirs(input_path)

                # create output directories for output scenarios, and only for the
                if sid in result_scenarios:
                    output_path = os.path.join(self.spatial_output_dir, 'Scenario-' + str(sid), 'Spatial')
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)

            if orig_scenarios is not None and sid not in result_scenarios:
                input_path = os.path.join(self.spatial_orig_input_dir, scenario_dir)
                if not os.path.exists(input_path):
                    os.makedirs(input_path)

    def exec_command(self, args, orig=False):
        """
        Executes a command to SyncroSim and returns a subprocess object.
        :param args: The arguments provided to the console
        :param orig: Use the original library to execute the command on.
        :return: subprocess object with stdout as a subprocess.PIPE (i.e. bytes) value.
        """
        if orig and "--import" in args:
            raise KeyError("Command ignored - importing into original library will corrupt data.")
        input_args = list()
        if len(self.prefix) > 0:
            input_args.append(self.prefix)
        input_args += (self.exe_orig_lib if orig else self.exe_lib)
        input_args += args
        return subprocess.run(input_args, stdout=subprocess.PIPE)

    def set_output_options(self, sid, working_path, **kwargs):
        """
        Sets the output options for a given scenario.
        :param sid: The scenario ID to set output options for.
        :param working_path: The temporary working path.
        :param kwargs: The settings to specify, using kwargs. These can be things like 'SummaryOutputSC' and 'RasterOutputSCTimesteps'.
        :return:
        """

        all_output_options = [
            "SummaryOutputSC", "SummaryOutputSCTimesteps", "SummaryOutputSCZeroValues",
            "SummaryOutputTR", "SummaryOutputTRTimesteps", "SummaryOutputTRIntervalMean",
            "SummaryOutputTRSC", "SummaryOutputTRSCTimesteps",
            "SummaryOutputSA", "SummaryOutputSATimesteps",
            "SummaryOutputTA", "SummaryOutputTATimesteps",
            "RasterOutputSC", "RasterOutputSCTimesteps",
            "RasterOutputTR", "RasterOutputTRTimesteps",
            "RasterOutputAge", "RasterOutputAgeTimesteps",
            "RasterOutputTST", "RasterOutputTSTTimesteps",
            "RasterOutputST", "RasterOutputSTTimesteps",
            "RasterOutputSA", "RasterOutputSATimesteps",
            "RasterOutputTA", "RasterOutputTATimesteps",
            "RasterOutputAATP", "RasterOutputAATPTimesteps"
        ]

        output_settings = dict()

        for kwarg in all_output_options:

            if kwarg in kwargs.keys():
                setting = 'Yes'
                if 'Timesteps' in kwarg:
                    setting = int(kwargs[kwarg])
            else:
                setting = ''

            output_settings[kwarg] = setting

        with open(working_path, 'w', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=all_output_options)
            writer.writeheader()
            writer.writerow(output_settings)

        self.import_sheet("STSim_OutputOptions", working_path, sid=sid, cleanup=False)

    def update_run_control(self, sid, working_path, spatial=False, iterations=5, start_timestep=0, end_timestep=20):

        if sid in self.list_scenarios(results_only=True):
            raise ValueError("Provided sid is a result scenario. Please use a non-scenario ID.")

        with open(working_path, 'w', newline='') as sheet:

            writer = csv.DictWriter(sheet, fieldnames=['MinimumIteration', 'MaximumIteration',
                                                       'MinimumTimestep', 'MaximumTimestep', 'IsSpatial'])
            writer.writeheader()
            writer.writerow({
                'MinimumIteration': 1,
                'MaximumIteration': int(iterations),
                'MinimumTimestep': int(start_timestep),
                'MaximumTimestep': int(end_timestep),
                'IsSpatial': 'Yes' if spatial else ''
            })

        self.import_sheet('STSim_RunControl', working_path, sid, cleanup=True)

    def list_scenario_names(self, results_only=None, orig=False):

        args = ["--list", "--scenarios"]
        output = self.exec_command(args, orig=orig).stdout.split(str.encode(self.sep))
        results = list()
        for line in output:
            if len(line.decode()) > 0:
                decoded = line.decode().split()
                if results_only and decoded[2] != '(Y)':
                    continue
                if " ".join(decoded[3:])[-2:] != 'M)':
                    scenario_name = " ".join(decoded[3:])
                else:
                    scenario_name = " ".join(decoded[3:-5])
                results.append({'sid': decoded[0], 'name':scenario_name, 'pid': decoded[1]})
        return results

    def list_scenarios(self, results_only=None, orig=False):
        """
        List scenarios from the .ssim library.
        :param results_only: Return only results scenarios
        :param orig: List results from the original library
        :return A list of scenario IDs from the library
        """

        args = ["--list", "--scenarios"]
        output = self.exec_command(args, orig=orig).stdout.split(str.encode(self.sep))
        results = list()
        for line in output:
            if len(line.decode()) > 0:
                decoded = line.decode().split()
                if results_only and decoded[2] != '(Y)':
                    continue
                results.append(decoded[0])
        return results

    def list_projects(self, orig=False):
        """
        List projects from the .ssim library
        :param orig: Return results from the original library
        :return: jA list of project IDs from the library
        """
        args = ["--list", "--projects"]
        output = self.exec_command(args, orig=orig).stdout.decode().split(self.sep)
        results = dict()
        for line in output:
            if len(line) > 0:
                parts = line.split()
                results[parts[0]] = " ".join(parts[1:])
        return results

    def list_datafeeds(self, orig=False):
        """
        List datafeeds from the .ssim library.
        :param orig: List results from the original library
        :return A list of available sheets from the given library
        """
        args = ["--list", "--datafeeds"]
        output = [x.split()[-1] for x in self.exec_command(args, orig=orig).stdout.decode().strip().split(self.sep)]
        return output

    def run_model(self, sid):
        """
        Performs a model run. Only runs models on the working library, not on the original library if specified.
        :param sid: The scenario to run the model for.
        :return: The result scenario ID from this model run.
        """

        if self.exe_orig_lib and str(sid) in self.list_scenarios(results_only=True):
            raise ValueError(str(sid) + ' is not an available scenario in the original (non-editable) library.')

        args = ["--run", "--sid=" + str(sid)]
        result_sid = self.exec_command(args).stdout.strip().split()[-1].decode()
        return result_sid

    def _use_sheet(self, action, sheet_name, path, sid=None, pid=None, orig=False):
        """
        Base function for executing transactions on a sheet
        :param action: The action to perform. Must be 'export' or 'import'
        :param sheet_name: The sheet to perform the action on.
        :param path: External file path to import from or export to.
        """

        action = '--' + action
        args = [action, "--sheet=" + sheet_name, "--file=" + path]
        if sheet_name in self.list_datafeeds(orig=orig):
            if str(pid) in self.list_projects().keys():
                args += ["--pid=" + str(pid)]
                self.exec_command(args, orig=orig)
            elif str(sid) in self.list_scenarios(orig=(action == 'import')):
                args += ["--sid=" + str(sid)]
                self.exec_command(args, orig=orig)
            else:
                raise ValueError("Scenario id is not available. Check list_scenarios() for available scenarios.")
        else:
            raise ValueError("Sheet name is not available. Check list_datafeeds() for available sheets.")

    def import_sheet(self, sheet_name, import_path, sid=None, pid=None, cleanup=False):
        """
        Import a sheet into a given scenario. Useful for setting initial conditions before a model run.
        :param sheet_name: Sheet to import into the given sid.
        :param import_path: Path to the sheet to import.
        :param sid: Scenario ID to apply the sheet to. Scenario ID and Project ID can't both be specified.
        :param pid: Project ID to apply the sheet to.
        :param cleanup: Delete the file after the file has been imported in.
        """

        self._use_sheet('import', sheet_name, import_path, sid=sid, pid=pid)
        if cleanup:
            os.remove(import_path)

    def export_sheet(self, sheet_name, export_path, sid=None, pid=None, overwrite=False, orig=False):
        """
        Export a sheet from a given scenario. Useful for collecting results that aren't generated in a report.
        :param sheet_name: Sheet to import into the given sid.
        :param export_path: Path to the sheet to export.
        :param sid: Scenario ID to extract the sheet from.
        :param overwrite: (Optional) Overwrite the file in the location.
        :param orig: Use the original library to export the sheet from.
        """

        if os.path.exists(export_path):
            if overwrite:
                os.remove(export_path)
            else:
                raise IOError("File exists and overwrite was set to False.")
        self._use_sheet('export', sheet_name, export_path, sid=sid, pid=pid, orig=orig)


class ReporterConsole(Console):
    """ Consoles that support reports """

    def list_reports(self):
        """List reports from a given console
        :return: A list of valid report types
        """

        args = ["--console=" + self.name, "--list-reports"]
        return [report.decode() for report in self.exec_command(args).stdout.strip().split()[2:]]

    def generate_report(self, report_type, out_path, sids):
        """
        Generates a report using the current console name and the provided report type, output path and scenario ID
        :param report_type: Name of the report to generate. Must be one available under self.reports
        :param out_path: Path to export the report to.
        :param sids: The scenario ID to execute the report on. Can be a single sid (str or int), a list of sids, or a
        numeric string of ids
        """

        # TODO - improve handling for different types of sids
        #if isinstance(sids, int):
        #    output_sids = str(sids)
        #elif isinstance(sids, list):
        #    output_sids = [str(sid) for sid in sids]

        if report_type in self.list_reports():
            if str(sids) in self.list_scenarios():

                # TODO - sids means we can output more than 1 report, so should output_sid be "".join([sid1, sid2, ...]) ?
                args = ["--console=" + self.name, "--create-report", "--name=" + report_type,
                        "--file=" + out_path, "--sids=" + str(sids)]
                self.exec_command(args)

            else:
                raise ValueError("Scenario id is not available. Check list_scenarios() for available scenarios.")
        else:
            raise ValueError(
                report_type.decode() + " is not a valid report type. Check list_reports() for available reports.")


# Here we create each reporter console with their given name
class STSimConsole(ReporterConsole):
    """ ST-Sim State and Transition Console class """

    name = 'stsim'

    def export_stateclass_definitions(self, pid, working_path, orig=False, readonly=False):
        if not readonly:
            self.export_sheet("STSim_StateClass", working_path, pid=pid, overwrite=True, orig=orig)
        with open(working_path, 'r') as sheet:
            reader = csv.DictReader(sheet)
            result_dict = dict()

            for row in reader:
                stateclass = row['Name']
                result_dict[stateclass] = {
                    'Development Stage': row['StateLabelXID'],
                    'Structural Stage': row['StateLabelYID'],
                    'ID': row['ID'],
                    'Color': row['Color'],
                    'Description': row['Description']
                }
            return OrderedDict(sorted(result_dict.items(), key=order()))

    def import_stateclass_definitions(self, pid, values_dict, working_path):
        if str(pid) not in self.list_projects().keys():
            raise ValueError('Project ID is not valid. Check .list_projects() for valid project values.')

        with open(working_path, 'w', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=['Name', 'StateLabelXID', 'StateLabelYID',
                                                       'ID', 'Color', 'Description'])
            writer.writeheader()
            for name in values_dict.keys():
                writer.writerow({
                    'Name': name,
                    'StateLabelXID': values_dict[name]['Development Stage'],
                    'StateLabelYID': values_dict[name]['Structural Stage'],
                    'ID': values_dict[name]['ID'],
                    'Color': values_dict[name]['Color'],
                    'Description': values_dict[name]['Description']
                })
        self.import_sheet('STSim_StateClass', working_path, pid=pid, cleanup=True)

    def export_vegtype_definitions(self, pid, working_path, orig=False, readonly=False):
        if not readonly:
            self.export_sheet("STSim_Stratum", working_path, pid=pid, overwrite=True, orig=orig)
        with open(working_path, 'r') as sheet:
            reader = csv.DictReader(sheet)
            result_dict = dict()
            for row in reader:
                vegtype = row['Name']
                result_dict[vegtype] = {
                    'ID': row['ID'],
                    'Color': row['Color'],
                    'Description': row['Description']
                }
            return OrderedDict(sorted(result_dict.items(), key=order()))

    def import_vegtype_definitions(self, pid, values_dict, working_path):
        if str(pid) not in self.list_projects():
            raise ValueError('Project ID is not valid. Check .list_projects() for valid project values.')

        with open(working_path, 'w', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=['Name', 'ID', 'Color', 'Description'])
            writer.writeheader()
            for name in values_dict.keys():
                writer.writerow({
                    'Name': name,
                    'ID': values_dict[name]['ID'],
                    'Color': values_dict[name]['Color'],
                    'Description': values_dict[name]['Description']
                })
        self.import_sheet('STSim_Stratum', working_path, pid=pid, cleanup=True)

    def export_stateclass_summary(self, sid, report_path=None, norm=1):

        path = report_path
        self.generate_report("stateclass-summary", path, sids=sid)
        with open(path, 'r') as report:
            reader = csv.DictReader(report)
            results_dict = dict()
            for row in reader:
                if row['Iteration'] not in results_dict:
                    results_dict[row['Iteration']] = dict()
                if row['Timestep'] not in results_dict[row['Iteration']]:
                    results_dict[row['Iteration']][row['Timestep']] = dict()
                if row['StratumID'] not in results_dict[row['Iteration']][row['Timestep']]:
                    results_dict[row['Iteration']][row['Timestep']][row['StratumID']] = dict()
                results_dict[row['Iteration']][row['Timestep']][row['StratumID']][row['StateClassID']] = str(float(row['ProportionOfLandscape']) * norm)
            return OrderedDict(sorted(results_dict.items(), key=order()))

    def export_det_transitions(self, sid, transitions_path, use_working_lib=False):

        path = transitions_path

        self.export_sheet("STSim_DeterministicTransition", path, sid=sid, overwrite=True,orig=not use_working_lib)

        with open(path, 'r') as sheet:

            reader = csv.DictReader(sheet)
            result_dict = dict()
            for row in reader:
                veg_type = row['StratumIDSource']
                if veg_type not in result_dict:
                    result_dict[veg_type] = list()
                result_dict[veg_type].append({'from': row['StateClassIDSource'], 'to': row['StateClassIDDest']})
            return OrderedDict(sorted(result_dict.items(), key=order()))

    def export_probabilistic_transitions_types(self, sid, transitions_path, readonly=False):

        path = transitions_path

        if not readonly:
            self.export_sheet("STSim_Transition", path, sid=sid, overwrite=True)

        with open(path, 'r') as sheet:

            reader = csv.DictReader(sheet)
            result_list = list()
            for row in reader:
                transition = row['TransitionTypeID']
                if transition not in result_list:
                    result_list.append(transition)

            return result_list

    def export_probabilistic_transitions_map(self, sid, transitions_path, orig=False, readonly=False):

        path = transitions_path
        if not readonly:
            self.export_sheet("STSim_Transition", path, sid=sid, overwrite=True, orig=orig)

        with open(path, 'r') as sheet:

            reader = csv.DictReader(sheet)
            result_dict = dict()
            for row in reader:
                veg_type = row['StratumIDSource']
                if veg_type not in result_dict:
                    result_dict[veg_type] = list()
                result_dict[veg_type].append({'from': row['StateClassIDSource'],
                                              'to': row['StateClassIDDest'],
                                              'type': row['TransitionTypeID'],
                                              'probability': float(row['Probability']),
                                              'age_reset': row['AgeReset']})
            return OrderedDict(sorted(result_dict.items(), key=order()))

    def import_probabilistic_transitions(self, sid, values_dict, working_path):

        path = working_path

        if str(sid) in self.list_scenarios(results_only=True):
            raise ValueError("Provided sid is a result scenario. Please use a non-scenario ID.")

        with open(path, 'w') as f_out:
            probabilities = csv.DictWriter(f_out,
                                           fieldnames=["StratumIDSource", "StateClassIDSource",
                                                       "StateClassIDDest", "TransitionTypeID",
                                                       "Probability", "AgeReset"])
            probabilities.writeheader()
            for veg_type in values_dict:
                for row in values_dict[veg_type]:
                    probabilities.writerow({"StratumIDSource": veg_type,
                                            "StateClassIDSource": row['from'],
                                            "StateClassIDDest": row['to'],
                                            "TransitionTypeID" : row['type'],
                                            "Probability": row['probability'],
                                            "AgeReset": row['age_reset']})
        try:
            self.import_sheet("STSim_Transition", path, sid=sid, cleanup=True)
        except:
            raise IOError("Malformed import sheet. Check " + path + " for errors.")

    def export_probabilistic_transitions_by_group(self, pid, working_path, readonly=False):

        if not readonly:
            self.export_sheet("STSim_TransitionTypeGroup", working_path, pid=pid, overwrite=True)

        with open(working_path, 'r') as sheet:

            reader = csv.DictReader(sheet)
            result_dict = dict()
            for row in reader:
                group = row['TransitionGroupID']
                if group not in result_dict:
                    result_dict[group] = list()
                result_dict[group].append(row['TransitionTypeID'])

        return OrderedDict(sorted(result_dict.items(), key=order()))

    def export_veg_state_classes(self, sid, state_class_path, readonly=False):

        path = state_class_path

        if not readonly:
            self.export_sheet("STSim_DeterministicTransition", path, sid=sid, overwrite=True)

        with open(path, 'r') as sheet:

            reader = csv.DictReader(sheet)
            result_dict = dict()
            for row in reader:
                veg_type = row['StratumIDSource']
                if veg_type not in result_dict:
                    result_dict[veg_type] = list()
                result_dict[veg_type].append(row['StateClassIDSource'])
            return OrderedDict(sorted(result_dict.items(), key=order()))

    def export_nonspatial_conditions(self, sid, working_path):

        self.export_sheet("STSim_InitialConditionsNonSpatial", working_path, sid=sid, overwrite=True)

        with open(working_path, 'r') as sheet:

            reader = csv.DictReader(sheet)

            try:
                return reader.__next__()
            except:
                return {field: '' for field in reader.fieldnames}

    def import_nonspatial_conditions(self, sid, values_dict, working_path):

        if str(sid) in self.list_scenarios(results_only=True):
            raise ValueError("Provided sid is a result scenario. Please use a non-scenario ID.")

        with open(working_path, 'w', newline='') as sheet:

            writer = csv.DictWriter(sheet, fieldnames=values_dict.keys())
            writer.writeheader()
            writer.writerow(values_dict)

        try:
            self.import_sheet("STSim_InitialConditionsNonSpatial", working_path, sid, cleanup=True)
        except:
            raise IOError("Malformed import sheet. Check " + working_path + " for errors.")

    def import_nonspatial_distribution(self, sid, values_dict, working_path):

        path = working_path

        if str(sid) in self.list_scenarios(results_only=True):
            raise ValueError("Provided sid is a result scenario. Please use a non-scenario ID.")

        with open(path, 'w', newline='') as f_out:
            initial_conditions = csv.DictWriter(f_out, fieldnames=["StratumID", "StateClassID", "RelativeAmount"])
            initial_conditions.writeheader()
            for veg_type in values_dict.keys():
                state_class_dict = values_dict[veg_type]
                for state_class in state_class_dict.keys():
                    value = state_class_dict[state_class]
                    initial_conditions.writerow({"StratumID": veg_type,
                                                 "StateClassID": state_class,
                                                 "RelativeAmount": float(value)})
        try:
            self.import_sheet("STSim_InitialConditionsNonSpatialDistribution", path, sid, cleanup=True)
        except:
            raise IOError("Malformed import sheet. Check " + path + " for errors.")

    def import_spatial_initial_conditions(self, sid, working_path, **kwargs):
        # TODO - make this generalized for various kinds of spatial inputs

        # state class and strata path must be specified
        if not all(path in kwargs and os.path.exists(kwargs[path]) for path in ['sc_path', 'strata_path']):
            raise KeyError('Given path to tif invalid or does not exist.')
        sc_path = kwargs.get('sc_path')
        strata_path = kwargs.get('strata_path')

        cleanup = kwargs.get('cleanup') if 'cleanup' in kwargs and isinstance(kwargs['cleanup'], bool) else False

        # copy the files to the input directory
        input_dir_path = os.path.join(self.spatial_input_dir, 'Scenario-'+str(sid),
                                      'STSim_InitialConditionsSpatial')
        sc_input_file = os.path.join(input_dir_path, 'sc_input.tif')
        strata_input_file = os.path.join(input_dir_path, 'stratum_input.tif')

        with rasterio.open(strata_path, 'r') as strata_src:
            strata_shape = strata_src.shape
            with rasterio.open(strata_input_file, 'w', **strata_src.profile) as dst:
                dst.write(strata_src.read(1), 1)

        with rasterio.open(sc_path, 'r') as sc_src:
            sc_shape = sc_src.shape
            affine = sc_src.affine
            srs = sc_src.crs.wkt
            with rasterio.open(sc_input_file, 'w', **sc_src.profile) as dst:
                dst.write(sc_src.read(1), 1)

        if strata_shape != sc_shape:
            raise ValueError('Shape mismatch between stateclass and stratum inputs.')

        if cleanup:
            os.remove(sc_path)
            os.remove(strata_path)

        initial_conditions_config = {
            'NumRows': sc_shape[0],
            'NumColumns': sc_shape[1],
            'NumCells': sc_shape[0] * sc_shape[1],
            'CellSize': 30,
            'CellSizeUnits': 'Meter',
            'CellArea': round(pow(30, 2)*M2_TO_ACRES, 4),
            'CellAreaOverride': '',
            'XLLCorner': affine[2],
            'YLLCorner': affine[5],
            'SRS': srs,
            'StratumFileName': 'stratum_input.tif',
            'StateClassFileName': 'sc_input.tif'
        }

        with open(working_path, 'w',  newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=initial_conditions_config.keys())
            writer.writeheader()
            writer.writerow(initial_conditions_config)

        self.import_sheet('STSim_InitialConditionsSpatial', working_path, str(sid), cleanup=True)

    def export_transition_group_types(self, pid, working_path, readonly=False):
        if not readonly:
            self.export_sheet('STSim_TransitionGroup', working_path, pid=pid, overwrite=True)

        with open(working_path) as sheet:
            reader = csv.DictReader(sheet)
            result_list = list()
            for row in reader:
                result_list.append(row['Name'])

        return result_list

    def export_transition_targets(self, sid, working_path, readonly=False):
        if not readonly:
            self.export_sheet('STSim_TransitionTarget', working_path, sid=sid, overwrite=True)

        with open(working_path) as sheet:
            reader = csv.DictReader(sheet)
            result_dict = dict()
            for row in reader:
                vegtype = row['StratumID']
                if vegtype not in result_dict.keys():
                    result_dict[vegtype] = list()
                result_dict[vegtype].append({
                    row['TransitionGroupID']: {
                        'iteration': row['Iteration'],
                        'timestep': row['Timestep'],
                        'amount': row['Amount']
                    }
                })

        return result_dict

    def import_transition_targets(self, sid, working_path, values_dict):
        path = working_path

        if str(sid) in self.list_scenarios(results_only=True):
            raise ValueError("Provided sid is a result scenario. Please use a non-scenario ID.")

        with open(path, 'w', newline='') as f_out:
            targets = csv.DictWriter(f_out, fieldnames=["Iteration", "Timestep", "StratumID",
                                                        "TransitionGroupID", "Amount"])
            targets.writeheader()
            for veg_type in values_dict.keys():
                transition_targets = values_dict[veg_type]    # list of transition targets
                for row in transition_targets:   # each target is a dictionary
                    transition_group = list(row.keys())[0]
                    targets.writerow({
                        'Iteration': row[transition_group]['iteration'],
                        'Timestep': row[transition_group]['timestep'],
                        'StratumID': veg_type,
                        'TransitionGroupID': transition_group,
                        'Amount': row[transition_group]['amount']
                    })
        try:
            self.import_sheet("STSim_TransitionTarget", path, sid=sid, cleanup=True)
            print('All done')
        except:
            raise IOError("Malformed import sheet. Check " + path + " for errors.")


class StockFlowConsole(ReporterConsole):
    """ Stocks and Flows Console class """

    name = 'stockflow'

    # TODO - Find use cases for Stocks and Flows
