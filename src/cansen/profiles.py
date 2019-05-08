# Standard libraries

# Third-party modules
import numpy as np


class VolumeProfile(object):
    """
    Set the velocity of the piston by using a user specified volume
    profile. The initialization and calling of this class are handled
    by the :py:class:`~cantera.Func1`
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

        :param t:
            Input float, current simulation time.
        """

        if t < self.time[-1]:
            # prev_time_point is the previous value in the time array
            # after the current simulation time
            prev_time_point = self.time[self.time <= t][-1]
            # index is the index of the time array where
            # prev_time_point occurs
            index = np.where(self.time == prev_time_point)[0][0]
            return self.velocity[index]
        else:
            return 0


class TemperatureProfile(object):
    """
    Set the temperature of the reactor by using a user specified
    temperature profile. The initialization and calling of this class
    are handled by the :py:class:`~cantera.Func1`
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
    are handled by the :py:class:`~cantera.Func1`
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

        # Angular velocity, rad/s
        self.omega = rev_per_minute*np.pi/30
        # Start angle, rad
        self.start_crank_rad = start_crank_angle/180.0*np.pi

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
        return (self.omega*self.stroke_length/2*np.sin(theta) *
                (1 + np.cos(theta)/np.sqrt(self.rod_radius_ratio**2 -
                                           np.sin(theta)**2)))


class PressureProfile(object):
    """
    Dummy class for the pressure profile, to be implemented in CanSen v2.0
    """
    pass
