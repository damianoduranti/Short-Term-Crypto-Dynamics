

class Coin_at_time:

    def __init__(self, date, time, open :float  , high:float, low:float, close:float, volume:float)->None:
        self._date = date
        self._time = time
        self._open = open
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume

    def __repr__(self) -> str:
        to_ret = { "date " : self._date,
                "time " : self._time,
                "open" : self._open,
                "high" : self._high, 
                "low" : self._low,
                "close" : self._close,
                "volume" : self._volume,}
        return str(to_ret)
    
    def feature_vector(self)-> list:
        return [self._open , self._high , self._low , self._close , self._volume]


class Coin_creator:
    
    def Coin_from_binance(raw_data:list):
        return Coin_at_time(raw_data[0],raw_data[1],raw_data[2],raw_data[3],raw_data[4],raw_data[5],raw_data[6],raw_data[7])

    def Coin_from_CSV(raw_data:list):
        return Coin_at_time(raw_data[0],raw_data[1],float(raw_data[2]),float(raw_data[3]),float(raw_data[4]),float(raw_data[5]), float(raw_data[6]))
    
    def Coin_from_DB(raw_data:list):
        return Coin_at_time(raw_data[0],raw_data[1],float(raw_data[2]),float(raw_data[3]),float(raw_data[4]),float(raw_data[5]), float(raw_data[6]))


"""List with max len"""

class list_max_len:

    def __init__(self, max_len) -> None:
        self._list = []
        self._max_len = max_len

    def access_list(self):
        return self._list

    def add(self, newel):
        if len(self._list) < self._max_len:
            self._list.append(newel)
        else:
            self._list.pop(0)
            self._list.append(newel)
