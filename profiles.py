try:    
    import numpy as np
except ImportError:
    print('Numpy must be installed')
    sys.exit(1)


class VolumeProfile(object):
    def __init__(self, keywords):
        self.time = np.array(keywords['vproTime'])
        self.volume = np.array(keywords['vproVol'])
        self.velocity = np.diff(self.volume)/np.diff(self.time)
        self.velocity = np.append(self.velocity,0)
    def __call__(self,t):
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
    def __init__(self,keywords):
        self.time = np.array(keywords['TproTime'])
        self.temperature = np.array(keywords['TproTemp'])
    def __call__(self,t):
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

class PressureProfile(object):
    pass
