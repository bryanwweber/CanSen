# Python 2 compatibility
from __future__ import print_function
from __future__ import division

# Standard libraries
import sys
import math

# More Python 2 compatibility
if sys.version_info.major == 3:
    from itertools import zip_longest
elif sys.version_info.major == 2:
    from itertools import izip_longest

# Related modules
try:
    import cantera as ct
except ImportError:
    print("Cantera must be installed")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print('NumPy must be installed')
    sys.exit(1)

try:
    import tables
except ImportError:
    print('PyTables must be installed')
    sys.exit(1)

# Local imports
from printer import divider
import utils
from profiles import (VolumeProfile, TemperatureProfile, PressureProfile,
                      ICEngineProfile)

class SimulationCase(object):
    """
    Class that sets up and runs a simulation case.
    """
    def __init__(self, filenames):
        """Initialize the simulation case.

        Read the SENKIN-format input file is read into the ``keywords``
        dictionary.

        :param filenames:
            Dictionary containing the relevant file names for this
            case.
        """
        self.input_filename = filenames['input_filename']
        self.mech_filename = filenames['mech_filename']
        self.save_filename = filenames['save_filename']
        self.thermo_filename = filenames['thermo_filename']

        self.keywords = utils.read_input_file(self.input_filename)

    def setup_case(self):
        """
        Sets up the case to be run. Initializes the ``ThermoPhase``,
        ``Reactor``, and ``ReactorNet`` according to the values from
        the input file.
        """
        self.gas = ct.Solution(self.mech_filename)

        initial_temp = self.keywords['temperature']
        # The initial pressure in Cantera is expected in Pa; in SENKIN
        # it is expected in atm, so convert
        initial_pres = self.keywords['pressure']*ct.one_atm
        # If the equivalence ratio has been specified, send the
        # keywords for conversion.
        if 'eqRatio' in self.keywords:
            reactants = utils.equivalence_ratio(
                self.gas,
                self.keywords['eqRatio'],
                self.keywords['fuel'],
                self.keywords['oxidizer'],
                self.keywords['completeProducts'],
                self.keywords['additionalSpecies'],
                )
        else:
            # The reactants are stored in the ``keywords`` dictionary
            # as a list of strings, so they need to be joined.
            reactants = ','.join(self.keywords['reactants'])

        self.gas.TPX = initial_temp, initial_pres, reactants

        # Create a non-interacting ``Reservoir`` to be on the other
        # side of the ``Wall``.
        env = ct.Reservoir(ct.Solution('air.xml'))
        # Set the ``temp_func`` to ``None`` as default; it will be set
        # later if needed.
        self.temp_func = None
        # All of the reactors are ``IdealGas`` Reactors. Set a ``Wall``
        # for every case so that later code can be more generic. If the
        # velocity is set to zero, the ``Wall`` won't affect anything.
        # We have to set the ``n_vars`` here because until the first
        # time step, ``ReactorNet.n_vars`` is zero, but we need the
        # ``n_vars`` before the first time step.
        if self.keywords['problemType'] == 1:
            self.reac = ct.IdealGasReactor(self.gas)
            # Number of solution variables is number of species + mass,
            # volume, temperature
            self.n_vars = self.reac.kinetics.n_species + 3
            self.wall = ct.Wall(self.reac, env, A=1.0, velocity=0)
        elif self.keywords['problemType'] == 2:
            self.reac = ct.IdealGasConstPressureReactor(self.gas)
            # Number of solution variables is number of species + mass,
            # temperature
            self.n_vars = self.reac.kinetics.n_species + 2
            self.wall = ct.Wall(self.reac, env, A=1.0, velocity=0)
        elif self.keywords['problemType'] == 3:
            self.reac = ct.IdealGasReactor(self.gas)
            # Number of solution variables is number of species + mass,
            # volume, temperature
            self.n_vars = self.reac.kinetics.n_species + 3
            self.wall = ct.Wall(self.reac, env, A=1.0,
                                velocity=VolumeProfile(self.keywords))
        elif self.keywords['problemType'] == 4:
            self.reac = ct.IdealGasConstPressureReactor(self.gas, energy='off')
            # Number of solution variables is number of species + mass,
            # temperature
            self.n_vars = self.reac.kinetics.n_species + 2
            self.wall = ct.Wall(self.reac, env, A=1.0, velocity=0)
        elif self.keywords['problemType'] == 5:
            self.reac = ct.IdealGasReactor(self.gas, energy='off')
            # Number of solution variables is number of species + mass,
            # volume, temperature
            self.n_vars = self.reac.kinetics.n_species + 3
            self.wall = ct.Wall(self.reac, env, A=1.0, velocity=0)
        elif self.keywords['problemType'] == 6:
            from user_routines import VolumeFunctionTime
            self.reac = ct.IdealGasReactor(self.gas)
            # Number of solution variables is number of species + mass,
            # volume, temperature
            self.n_vars = self.reac.kinetics.n_species + 3
            self.wall = ct.Wall(self.reac, env, A=1.0,
                                velocity=VolumeFunctionTime())
        elif self.keywords['problemType'] == 7:
            from user_routines import TemperatureFunctionTime
            self.reac = ct.IdealGasConstPressureReactor(self.gas, energy='off')
            # Number of solution variables is number of species + mass,
            # temperature
            self.n_vars = self.reac.kinetics.n_species + 2
            self.wall = ct.Wall(self.reac, env, A=1.0, velocity=0)
            self.temp_func = ct.Func1(TemperatureFunctionTime())
        elif self.keywords['problemType'] == 8:
            self.reac = ct.IdealGasConstPressureReactor(self.gas, energy='off')
            # Number of solution variables is number of species + mass,
            # temperature
            self.n_vars = self.reac.kinetics.n_species + 2
            self.wall = ct.Wall(self.reac, env, A=1.0, velocity=0)
            self.temp_func = ct.Func1(TemperatureProfile(self.keywords))
        elif self.keywords['problemType'] == 9:
            self.reac = ct.IdealGasReactor(self.gas)
            # Number of solution variables is number of species + mass,
            # volume, temperature
            self.n_vars = self.reac.kinetics.n_species + 3
            self.wall = ct.Wall(env, self.reac, A=1.0,
                                velocity=ICEngineProfile(self.keywords))

        if 'reactorVolume' in self.keywords:
            self.reac.volume = self.keywords['reactorVolume']

        # Create the Reactor Network.
        self.netw = ct.ReactorNet([self.reac])

        if 'sensitivity' in self.keywords:
            self.sensitivity = True
            # There is no automatic way to calculate the sensitivity of
            # all of the reactions, so do it manually.
            for i in range(self.reac.kinetics.n_reactions):
                self.reac.add_sensitivity_reaction(i)
            # If no tolerances for the sensitivity are specified, set
            # to the SENKIN defaults.
            if 'sensAbsTol' in self.keywords:
                self.netw.atol_sensitivity = self.keywords['sensAbsTol']
            else:
                self.netw.atol_sensitivity = 1.0E-06
            if 'sensRelTol' in self.keywords:
                self.netw.rtol_sensitivity = self.keywords['sensRelTol']
            else:
                self.netw.rtol_sensitivity = 1.0E-04
        else:
            self.sensitivity = False

        # If no solution tolerances are specified, set to the default
        # SENKIN values.
        if 'abstol' in self.keywords:
            self.netw.atol = self.keywords['abstol']
        else:
            self.netw.atol = 1.0E-20

        if 'reltol' in self.keywords:
            self.netw.rtol = self.keywords['reltol']
        else:
            self.netw.rtol = 1.0E-08


        if 'tempLimit' in self.keywords:
            self.temp_limit = self.keywords['tempLimit']
        else:
            # tempThresh is set in the parser even if it is not present
            # in the input file
            self.temp_limit = (self.keywords['tempThresh'] +
                               self.keywords['temperature'])

        self.tend = self.keywords['endTime']

        # Set the maximum time step the solver can take. If a value is
        # not specified in the input file, default to 0.001*self.tend.
        # Set the time steps for saving to the binary file and writing
        # to the screen. If the time step for printing to the screen is
        # not set, default to printing 100 times.
        print_time_int = self.keywords.get('prntTimeInt')
        save_time_int = self.keywords.get('saveTimeInt')
        max_time_int = self.keywords.get('maxTimeStep')

        time_ints = [value for value in
                        [print_time_int, save_time_int, max_time_int]
                        if value is not None
                    ]

        if time_ints:
            self.netw.set_max_time_step(min(time_ints))
        else:
            self.netw.set_max_time_step(self.tend/100)

        if print_time_int is not None:
            self.print_time_step = print_time_int
        else:
            self.print_time_step = self.tend/100

        self.print_time = self.print_time_step

        self.save_time_step = save_time_int

        if self.save_time_step is not None:
            self.save_time = self.save_time_step

        # Store the species names in a slightly shorter variable name
        self.species_names = self.reac.thermo.species_names

        #Initialize the ignition time, in case the end time is reached
        # before ignition occurs
        self.ignition_time = None

    def run_case(self):
        """
        Actually run the case set up by ``setup_case``. Sets binary
        output file format, then runs the simulation by using
        ``ReactorNet.step(self.tend)``.
        """
        # Use the table format of hdf instead of the array format. This
        # way, each variable can be saved in its own column and
        # referenced individually when read. Solution to the
        # interpolation problem was made by saving the most recent time
        # steps into numpy arrays. The arrays are not vertically
        # appended so we should eliminate the hassle associated with
        # that.
        table_def = {'time':tables.Float64Col(pos=0),
                     'temperature':tables.Float64Col(pos=1),
                     'pressure':tables.Float64Col(pos=2),
                     'volume':tables.Float64Col(pos=3),
                     'massfractions':tables.Float64Col(
                          shape=(self.reac.thermo.n_species), pos=4
                          ),
                     }
        if self.sensitivity:
            table_def['sensitivity'] = tables.Float64Col(
                shape=(self.n_vars, self.netw.n_sensitivity_params), pos=5
                )

        with tables.open_file(self.save_filename, mode='w',
                title='CanSen Save File') as save_file:
            table = save_file.create_table(save_file.root, 'reactor',
                                           table_def, 'Reactor State'
                                           )
            # Create a row instance to save information to.
            timestep = table.row
            # Save information before the first time step.
            timestep['time'] = self.netw.time
            (timestep['temperature'], timestep['pressure'],
                timestep['massfractions']) = self.reac.thermo.TPY
            timestep['volume'] = self.reac.volume
            if self.sensitivity:
                timestep['sensitivity'] = np.zeros((self.n_vars,
                                              self.netw.n_sensitivity_params))
            # Add the ``timestep`` to the ``table`` and write it to
            # disk.
            timestep.append()
            table.flush()
            # Set an array with values from before the first time step
            # in case we have to interpolate after the first time step
            prev_time = np.hstack((self.netw.time, self.reac.thermo.T,
                                   self.reac.thermo.P, self.reac.volume,
                                   self.wall.vdot(self.netw.time),
                                   self.reac.thermo.X
                                   ))
            # Print the initial information to the screen
            print(divider)
            print('Kinetic Mechanism Details:\n')
            print(('Total Gas Phase Species     = {0}\n'
                   'Total Gas Phase Reactions   = {1}'
                   ).format(self.reac.kinetics.n_species,
                   self.reac.kinetics.n_reactions))
            if self.sensitivity:
                print(('Total Sensitivity Reactions = {}'
                       ).format(self.netw.n_sensitivity_params))
            print(divider, '\n')

            self.reactor_state_printer(prev_time)

            ignition_found = False

            # Main loop to run the calculation. As long as the time in
            # the ``ReactorNet`` is less than the end time, keep going.
            while self.netw.time < self.tend:
                # If we are using a function to set the temperature as
                # a function of time, use it here.
                if self.temp_func is not None:
                    self.gas.TP = self.temp_func(self.netw.time), None

                # Take the step towards the end time.
                self.netw.step(self.tend)

                # Set an array with the information from the current
                # time step for printing.
                cur_time = np.hstack((self.netw.time, self.reac.thermo.T,
                                      self.reac.thermo.P, self.reac.volume,
                                      self.wall.vdot(self.netw.time),
                                      self.reac.thermo.X
                                      ))

                # If we have passed the end time, interpolate backwards
                # to get the solution at the end time. Because linear
                # interpolation is used, this will not work well if the
                # end time is during or before the ignition event and
                # we have stepped past it. This is unlikely though, as
                # the solver should be taking relatively small time
                # steps near ignition.
                if self.netw.time > self.tend:
                    interp_state = utils.reactor_interpolate(self.tend,
                                                             prev_time,
                                                             cur_time)
                    self.reactor_state_printer(interp_state, end=True)
                    timestep['time'] = self.tend
                    timestep['temperature'] = interp_state[1]
                    timestep['pressure'] = interp_state[2]
                    # Mass fractions are saved, so convert the mole
                    # fractions in ``interp_state`` to mass fractions.
                    timestep['massfractions'] = \
                        (interp_state[5:] *
                         self.reac.thermo.molecular_weights /
                         self.reac.thermo.mean_molecular_weight)

                    timestep['volume'] = interp_state[3]
                    if self.sensitivity:
                        # Add sensitivity interpolation here by reading
                        # from file on disk. Only have to do it once,
                        # so it shouldn't be too expensive.
                        prev_sens = table.cols.sensitivity[-1]
                        cur_sens = self.netw.sensitivities()
                        prev_time = table.cols.time[-1]
                        cur_time = self.netw.time
                        interp_sens = prev_sens + ((self.tend - prev_time) *
                                                   (cur_sens - prev_sens) /
                                                   (cur_time - prev_time))
                        timestep['sensitivity'] = interp_sens
                    # We don't need any of the rest of this step, so
                    # break
                    break

                # If the ``save_time_step`` is set, save at the nearest
                # step to the given interval. To avoid any errors, the
                # values written to the binary save file will not be
                # interpolated, but saved at the solver time step
                # instead. If ``save_time_step`` is not set, save every
                # time step to the binary file.
                if self.save_time_step is not None:
                    # Add what to do here if the save_time_step is set.
                    if self.netw.time > self.save_time:
                        timestep['time'] = self.netw.time
                        (timestep['temperature'], timestep['pressure'],
                            timestep['massfractions']) = self.reac.thermo.TPY
                        timestep['volume'] = self.reac.volume
                        if self.sensitivity:
                            timestep['sensitivity'] = self.netw.sensitivities()
                        timestep.append()
                        table.flush()
                        self.save_time += self.save_time_step
                else:
                    timestep['time'] = self.netw.time
                    (timestep['temperature'], timestep['pressure'],
                        timestep['massfractions']) = self.reac.thermo.TPY
                    timestep['volume'] = self.reac.volume
                    if self.sensitivity:
                        timestep['sensitivity'] = self.netw.sensitivities()
                    timestep.append()
                    table.flush()

                # Print Reactor state information to the screen for
                # monitoring.
                if self.netw.time > self.print_time:
                    interp_state = utils.reactor_interpolate(self.print_time,
                                                             prev_time,
                                                             cur_time)
                    self.reactor_state_printer(interp_state)
                    self.print_time += self.print_time_step
                elif self.netw.time == self.print_time:
                    self.reactor_state_printer(cur_time)
                    self.print_time += self.print_time_step

                # If the temperature limit has been exceeded, we have
                # ignition! Save the time this occurs at. In the
                # future, the ignition time may be interpolated.
                if self.reac.T >= self.temp_limit and ignition_found == False:
                    self.ignition_time = self.netw.time
                    ignition_found = True
                    if self.keywords.get('break_on_ignition', False):
                        self.reactor_state_printer(cur_time, end=False)
                        break

                # Set the ``prev_time`` array equal to the ``cur_time``
                # array so we can go to the next time step.
                prev_time = cur_time

    def run_simulation(self):
        """
        Helper function that sequentially sets up the simulation case
        and runs it. Useful for cases where nothing needs to be changed
        between the setup and run. See `setup_case` and `run_case`.
        """
        self.setup_case()
        self.run_case()


    def reactor_state_printer(self, state, end=False):
        """Produce pretty-printed output from the input reactor state.

        In this function, we have to explicitly pass in the reactor
        state instead of using ``self.reac`` because we might have
        interpolated to get to the proper time.

        :param state:
            Vector of reactor state information.
        :param end:
            Boolean to tell the printer this is the final print operation.
        """
        time = state[0]
        temperature = state[1]
        pressure = state[2]
        volume = state[3]
        vdot = state[4]
        molefracs = state[5:]

        # Begin printing
        print(divider)
        if not end:
            print('Solution time (s) = {:E}'.format(time))
        else:
            print('End time reached (s) = {:E}'.format(time))

        if self.ignition_time is not None:
            print('Ignition time (s) = {:E}'.format(self.ignition_time))
        elif end:
            print('Ignition was not found.')
        else:
            pass

        print(("Reactor Temperature (K) = {0:>13.4f}\n"
            "Reactor Pressure (Pa)   = {1:>13.4E}\n"
            "Reactor Volume (m**3)   = {2:>13.4E}\n"
            "Reactor Vdot (m**3/s)   = {3:>13.4E}"
            ).format(temperature, pressure, volume, vdot))
        print('Gas Phase Mole Fractions:')

        # Here we calculate the number of columns of species mole fractions
        # that will best fill the available number of columns in the
        # terminal.
        #
        # Add one to the max_species_length to ensure that there is at
        # least one space between species.
        max_species_length = len(max(self.species_names, key=len)) + 1
        # Set the precision of the printed mole fractions. This is the
        # number of columns that the number itself will take up, including
        # the decimal separator. It is not the field width.
        mole_frac_precision = 8
        # Calculate how much space each species print will take. It is the
        # max_species length + len(' = ') + the mole_frac_precision +
        # len('E+00').
        part_length = max_species_length + 3 + mole_frac_precision + 4
        # Set the default number of columns in the terminal. Choose 80
        # because it is the preferred width of Python source code, and
        # putting a bigger number may make the output text file harder
        # to read.
        cols = 80
        # Calculate the optimum number of columns as the floor of the
        # quotient of the print columns and the part_length
        num_print_cols = int(math.floor(cols/part_length))
        # Create a list to store the values to be printed.
        outlist = []
        for species_name, mole_frac in zip(self.species_names, molefracs):
            outlist.append('{0:>{1}s} = {2:{3}E}'.format(species_name,
                                                        max_species_length,
                                                        mole_frac,
                                                        mole_frac_precision)
                                                        )
        if sys.version_info.major == 3:
            grouped = zip_longest(*[iter(outlist)]*num_print_cols,
                                  fillvalue='')
        elif sys.version_info.major == 2:
            grouped = izip_longest(*[iter(outlist)]*num_print_cols,
                                   fillvalue='')
        for items in grouped:
            for item in items:
                print(item, end='')
            print('\n', end='')
        print(divider, '\n')

class MultiSimulationCase(SimulationCase):
    """Class that sets up and runs a simulation case, for multiple.

    When multiple cases are run, no output is printed and no simulation
    data is saved; upon completion, the calculated ignition delay times
    are written to the output file.
    """

    def __init__(self, filenames):
        """Initialize the simulation case.

        Read the SENKIN-format input file is read into the ``keywords``
        dictionary.

        :param filenames:
            Dictionary containing the relevant file names for this
            case.
        """
        self.input_filename = filenames['input_filename']
        self.mech_filename = filenames['mech_filename']
        self.save_filename = filenames['save_filename']
        self.thermo_filename = filenames['thermo_filename']

        self.keywords = utils.read_input_file(self.input_filename)


    def run_case(self):
        """
        Actually run the case set up by ``setup_case``. Runs the
        simulation by using ``ReactorNet.step(self.tend)``.
        """

        ignition_found = False

        # Main loop to run the calculation. As long as the time in
        # the ``ReactorNet`` is less than the end time, keep going.
        while self.netw.time < self.tend:
            # If we are using a function to set the temperature as
            # a function of time, use it here.
            if self.temp_func is not None:
                self.gas.TP = self.temp_func(self.netw.time), None

            # Take the step towards the end time.
            self.netw.step(self.tend)

            # If the temperature limit has been exceeded, we have
            # ignition! Save the time this occurs at. In the
            # future, the ignition time may be interpolated.
            if self.reac.T >= self.temp_limit and ignition_found == False:
                self.ignition_time = self.netw.time
                ignition_found = True
                break

