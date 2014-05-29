class VolumeFunctionTime(object):
    """
    Calculate the volume of the reactor as a user specified function 
    of time.
    """
    def __init__(self):
        """Set up the function to be calculated.
        
        The init function should be used to import any parameters for 
        the volume as a function of time from external files. Do not
        calculate the volume as a function of time here. Store all of
        the parameters in the ``self`` instance. The reason for this is 
        to avoid running the ``__init__`` function on every time step.
        See the example below.
        
        Example to load polynomial parameters from a file::
        
            # Read the file into the list ``self.params``. The lines of 
            # the file are read as strings.
            with open('file.txt','r') as input_file:
                self.params = input_file.readlines()
            # Convert the strings to floats.
            self.params = [float(param) for param in self.params]
            self.area = 1 # m**2
        """
        pass
        
    def __call__(self, time):
        """Return the velocity of the piston at the given time.
        
        The call function should be where the implementation of the
        volume as a function of time is done. Cantera expects the 
        velocity to be returned - v = dV/dt * 1/A. Get all of the
        needed parameters that were stored in the ``self`` instance.
        See the example below.
        
        Example to use the previously stored polynomial parameters::
        
            volume = (self.params[0] + self.params[1]*time + 
                self.params[2]*time**2 + self.params[3]*time**3) # m**3
            dvoldt = (self.params[1] + 2*self.params[2]*time + 
                3*self.params[3]*time**2) # m**3/s
            velocity = dvoldt/self.area # m/s
            return velocity 
        """
        return 0
    
class TemperatureFunctionTime(object):
    """
    Calculate the temperature of the reactor as a user specified 
    function of time.
    """
    def __init__(self):
        """Set up the function to be calculated.
        
        The init function should be used to import any parameters for 
        the temperature as a function of time from external files. Do not
        calculate the temperature as a function of time here. Store all of
        the parameters in the ``self`` instance. The reason for this is 
        to avoid running the ``__init__`` function on every time step.
        See the example below.
        
        Example to load polynomial parameters from a file::
        
            # Read the file into the list ``self.params``. The lines of 
            # the file are read as strings.
            with open('file.txt','r') as input_file:
                self.params = input_file.readlines()
            # Convert the strings to floats.
            self.params = [float(param) for param in self.params]
        """
        pass
        
    def __call__(self, time):
        """Return the temperature of the piston at the given time.
        
        The call function should be where the implementation of the
        temperature as a function of time is done. Get all of the
        needed parameters that were stored in the ``self`` instance.
        See the example below. Note: ``None`` is not a valid return
        value, so this function does not work as written.
        
        Example to use the previously stored polynomial parameters::
        
            temperature = (self.params[0] + self.params[1]*time + 
                self.params[2]*time**2 + self.params[3]*time**3) # K
            return temperature 
        """
        return None
        
