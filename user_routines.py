class VolumeFunctionTime(object):
    def __init__(self):
        """
        The init function should be used to import any parameters
        for the volume as a function of time from external files
        """
        pass
    def __call__(self,time):
        """
        The call function should be where the implementation of the
        volume as a function of time is done.
        """
        return 0
    
class TemperatureFunctionTime(object):
    def __init__(self):
        """
        The init function should be used to import any parameters
        for the temperature as a function of time from external files
        """ 
        pass
    def __call__(self,time):
        """
        The call function should be where the implementation of the
        temperature as a function of time is done.
        """
        return None
    def run_simulation(self):
        """
        This method actually runs the simulation. For now it is a dummy
        method, pending a decision about how to run the simulation. May
        be deleted at any point.
        """
        pass
    