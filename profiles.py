# Standard libraries
import sys

# Related modules
try:
    import numpy as np
except ImportError:
    print('NumPy must be installed')
    sys.exit(1)


class VolumeProfile(object):
    """
    Set the velocity of the piston by using a user specified volume
    profile. The initialization and calling of this class are handled
    by the `Func1 <http://cantera.github.io/docs/sphinx/html/cython/zerodim.html#cantera.Func1>`_
    interface of Cantera. Used with the input keyword :ref:`VPRO <VPRO>`
    """
    def __init__(self, keywords):
        """Set the initial values of the arrays from the input keywords.

        The time and volume are read from the input file and stored in
        the ``keywords`` dictionary. The velocity is calculated by
        assuming a unit area and using the forward difference,
        calculated by ``numpy.diff``. This function is only called
        once when the class is initialized at the beginning of a
        problem so it is efficient.

        :param keywords:
            Dictionary of keywords read from the input file
        """
        # The time and volume are stored as lists in the keywords
        # dictionary. The volume is normalized by the first volume
        # element so that a unit area can be used to calculate the
        # velocity.
        self.time = np.array(keywords['vproTime'])
        self.volume = np.array(keywords['vproVol'])/keywords['vproVol'][0]

        # The velocity is calculated by the forward difference.
        # numpy.diff returns an array one element smaller than the
        # input array, so we append a zero to match the length of the
        # self.time array.
        self.velocity = np.diff(self.volume)/np.diff(self.time)
        self.velocity = np.append(self.velocity, 0)

    def __call__(self, t):
        """Return the velocity when called during a time step.

        Using linear interpolation, determine the velocity at a given
        input time ``t``.

        :param t:
            Input float, current simulation time.
        """
        if t == 0:
            return 0
        if t < self.time[1]:
            tim0 = self.time[0]
            tim1 = self.time[1]
            vel0 = self.velocity[0]
            vel1 = self.velocity[1]
        elif t >= self.time[1] and t <= self.time[-1]:
            tim0 = self.time[self.time < t][-1]
            tim1 = self.time[np.where(self.time == tim0)[0][0]+1]
            vel0 = self.velocity[self.time < t][-1]
            vel1 = self.velocity[np.where(self.time == tim0)[0][0]+1]
        elif t > self.time[-1]:
            return 0

        interp = vel0 + (vel1-vel0)*(t-tim0)/(tim1-tim0)
        return interp

class TemperatureProfile(object):
    """
    Set the temperature of the reactor by using a user specified
    temperature profile. The initialization and calling of this class
    are handled by the  `Func1 <http://cantera.github.io/docs/sphinx/html/cython/zerodim.html#cantera.Func1>`_
    interface of Cantera. Used with the input keyword :ref:`TPRO <TPRO>`
    """
    def __init__(self, keywords):
        """Set the initial values of the arrays from the input keywords.

        The time and temperature are read from the input file and
        stored in the ``keywords`` dictionary as lists. This function
        is only called once when the class is initialized at the
        beginning of a problem so it is efficient.
        """
        self.time = np.array(keywords['TproTime'])
        self.temperature = np.array(keywords['TproTemp'])

    def __call__(self, t):
        """Return the temperature when called during a time step.

        Using linear interpolation, determine the temperature at a
        given input time ``t``.

        :param t:
            Input float, current simulation time.
        """
        if t == 0:
            return self.temperature[0]
        if t < self.time[1]:
            tim0 = self.time[0]
            tim1 = self.time[1]
            temp0 = self.temperature[0]
            temp1 = self.temperature[1]
        elif t >= self.time[1] and t <= self.time[-1]:
            tim0 = self.time[self.time < t][-1]
            tim1 = self.time[np.where(self.time == tim0)[0][0]+1]
            temp0 = self.temperature[self.time < t][-1]
            temp1 = self.temperature[np.where(self.time == tim0)[0][0]+1]
        elif t > self.time[-1]:
            return self.temperature[-1]

        interp = temp0 + (temp1-temp0)*(t-tim0)/(tim1-tim0)
        return interp

class ICEngineProfile(object):
    """
    Set the velocity of the wall according to the parameters of a
    reciprocating engine. The initialization and calling of this class
    are handled by the  `Func1 <http://cantera.github.io/docs/sphinx/html/cython/zerodim.html#cantera.Func1>`_
    interface of Cantera. Used with the input keyword :ref:`ICEN <ICEN>`.
    """
    def __init__(self, keywords):
        """Set the initial values of the engine parameters.

        The parameters are read from the input file into the
        ``keywords`` dictionary.
        """
        start_crank_angle = keywords.get('start_crank_angle', 180.0)
        self.rod_radius_ratio = keywords['rod_radius_ratio']
        rev_per_minute = keywords['rev_per_min']
        self.stroke_length = keywords['stroke_length']

        self.omega = rev_per_minute * np.pi / 30 # Angular velocity, rad/s
        self.start_crank_rad = start_crank_angle/180.0*np.pi # Start angle, rad

    def __call__(self, time):
        """Return the velocity of the piston when called.

        The function for the velocity is given by Heywood.
        See :doc:`/icengine`.

        :param time:
            Input float, current simulation time
        """
        theta = self.start_crank_rad - self.omega * time

        # Technically, this is negative, but the way we install the
        # wall between the reactor and the environment handles the
        # sign.
        velocity = (self.omega*self.stroke_length/2*np.sin(theta)*
                    (1 + np.cos(theta)/np.sqrt(self.rod_radius_ratio**2 -
                                               np.sin(theta)**2)))
        return velocity

class PressureProfile(object):
    """
    Dummy class for the pressure profile, to be implemented in CanSen v2.0
    """
    pass
