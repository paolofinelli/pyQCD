import cPickle
import zipfile
import os
import numpy as np
import numpy.random as npr

class DataSet:
    # Generic data set class. Contains header that denotes type of data.
    # Routines to perform statistical measurements on the entire dataset
    def __init__(self, datatype, filename, compress=True):
        """Create an empty data set holding data of the specified type
        
        :param datatype: The data type stored in the data set
        :type datatype: :class:`type`
        :param filename: The zip file to save the data to
        :type filename: :class:`str`
        :param compress: Determines whether compression is used
        :type compress: :class:`bool`
        :returns: :class:`DataSet`
        :raises: RuntimeError
        """
        
        storage_mode = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
        
        self.datatype = datatype
        self.num_data = 0
        self.filename = filename
        self.jackknifes_cached = False
        
        try:
            zfile = zipfile.ZipFile(filename, 'w', storage_mode, True)
            self.large_file = True
        except RuntimeError:
            print("Warning: > 2GB data set not supported.")
            storage_mode = zipfile.ZIP_STORED
            zfile = zipfile.ZipFile(filename, 'w', storage_mode, False)
            self.large_file = False
            
        self.storage_mode = storage_mode
        
        typefile = open("type", 'w')
        cPickle.dump(datatype, typefile)
        typefile.close()
        
        zfile.write("type")
        zfile.close()
        os.unlink("type")
    
    def add_datum(self, datum):
        """Adds a datum to the dataset
        
        :param datum: The data to add
        :type datum: The type specified in the object constructor
        :raises: TypeError
        """
        
        if type(datum) != self.datatype:
            raise TypeError("Supplied data type {} does not match the required "
                            "data type {}".format(type(datum), self.datatype))
        
        datum.save("{}{}".format(self.datatype.__name__, self.num_data))
        
        with zipfile.ZipFile(self.filename, 'a', self.storage_mode,
                             self.large_file) as zfile:
            zfile.write("{}{}.npz".format(self.datatype.__name__, self.num_data))
        
        os.unlink("{}{}.npz".format(self.datatype.__name__, self.num_data))
        self.num_data += 1
    
    def get_datum(self, index):
        """Retrieves the specified datum from the zip archive
        
        :param index: The index of the item to be retrieved
        :type index: :class:`int`
        :returns: The datum as the type specified in the constructor
        """
        
        filename = "{}{}.npz".format(self.datatype.__name__, index)
        
        with zipfile.ZipFile(self.filename, 'r', self.storage_mode,
                             self.large_file) as zfile:
            zfile.extract(filename)
            
        output = self.datatype.load(filename)
        os.unlink(filename)
        
        return output
    
    def set_datum(self, index, datum):
        """Sets the specified datum to the specified value
        
        :param index: The index of the item being set
        :type index: :class:`int`
        :param datum: The value used to set the specified datum to
        :type datum: The type specified in the object constructor
        :raises: ValueError
        """
        
        if type(datum) != self.datatype:
            raise TypeError("Supplied data type {} does not match the required "
                            "data type {}".format(type(datum), self.datatype))
        
        if index >= self.num_data:
            raise TypeError("Datum {} does not exist".format(index))
        
        filename = "{}{}.npz".format(self.datatype.__name__, self.num_data)
        
        datum.save(filename[:-4])
        
        with zipfile.ZipFile(self.filename, 'a', self.storage_mode,
                             self.large_file) as zfile:
            zfile.write(filename)
            
        os.unlink(filename)
        
    def apply_function(self, func, args):
        """Applies the specified function to each datum in the dataset before
        saving each new datum over the original
        
        :param function: The function to apply
        :type function: :class:`function`
        :param args: The function arguments
        :type args: :class:`list`
        """
        
        for i in xrange(self.num_data):
            datum = self.get_datum(i)
            new_datum = func(datum, *args)
            self.set_datum(i, new_datum)
    
    def measure(self, func, data=[], args=[]):
        """Performs a measurement on each item in the data set using the
        supplied function and returns the average of the measurements
        
        :param func: The measurement function, whose first argument is the datum object on which to perform the measurement
        :type func: :class:`function`
        :param data: The data indices to perform the measurement on
        :type data: :class:`list`
        :param args: The arguments required by the supplied function
        :type args: :class:`list`
        """

        if data == []:
            data = range(self.num_data)
            
        datum_sum = self.get_datum(data[0])

        for i in data[1:]:
            datum_sum += self.get_datum(i)
                
        datum_sum /= len(data)
        measurement = func(datum_sum, *args)
        
        return measurement
    
    def statistics(self):
        """Computes and returns the mean and standard deviation of the data within
        the dataset
        
        :returns: :class:`tuple` of types stored within current dataset
        """
        
        data_sum = self.get_datum(0)
        
        for i in xrange(self.num_data):
            data_sum += self.get_datum(i)
            
        data_mean = data_sum / self.num_data
        
        data_std = (self.get_datum(0) - data_mean)**2
        
        for i in xrange(self.num_data):
            data_std += (self.get_datum(i) - data_mean)**2
                
        data_std /= self.num_data
        
        return data_mean, data_std**0.5
    
    def bootstrap(self, func, num_bootstraps, binsize=1, args=[]):
        """Performs a bootstraped measurement on the dataset using the
        supplied function
        
        :param func: The measurement function
        :type func: :class:`function`
        :param binsize: The bin size used when binning
        :type binsize: :class:`int`
        :param num_bootstraps: The number of bootstraps to perform
        :type num_bootstraps: :class:`int`
        :param args: The arguments required by the supplied function
        :type args: :class:`list`
        """
        
        if binsize < 1:
            raise ValueError("Supplied bin size {} is less than 1"
                             .format(binsize))
        
        num_bins = self.num_data / binsize
        if self.num_data % binsize > 0:
            num_bins += 1
            
        out = []
        
        for i in xrange(num_bootstraps):
            
            bins = npr.randint(num_bins, size = num_bins).tolist()
            
            new_datum = self._get_bin(binsize, bins[0])
            for b in bins[1:]:
                new_datum += self._get_bin(binsize, b)
                
            new_datum /= len(bins)
            measurement = func(new_datum, *args)
            if measurement != None:                
                out.append(measurement)
            
        return DataSet._mean(out), DataSet._std(out)
    
    def jackknife_datum(self, index, binsize=1):
        """Computes a jackknifed datum
        
        :param index: The configuration to remove when computing the jackknife
        :type index: :class:`int`
        :param binsize: The bin size to use when binning
        :type binsize: :class:`int`
        :raises: ValueError
        """
        
        if binsize < 1:
            raise ValueError("Supplied bin size {} is less than 1"
                             .format(binsize))
        
        if index >= self.num_data:
            raise ValueError("Supplied index {} is greater than the number of "
                             "data {}"
                             .format(index, self.num_data))
        
        num_bins = self.num_data / binsize
        if self.num_data % binsize > 0:
            num_bins += 1
        
        data_sum = self._get_bin(binsize, 0)
        for i in xrange(1, num_bins):
            data_sum += self._get_bin(binsize, i)
            
        return (data_sum - self._get_bin(binsize, index)) / (num_bins - 1)
    
    def generate_jackknife_cache(self, binsize=1):
        """Generates the jackknifed data and stores it in the folder cache
        
        :param binsize: The bin size to use when handling the data
        :type binsize: :class:`int`
        """
        
        if binsize < 1:
            raise ValueError("Supplied bin size {} is less than 1"
                             .format(binsize))
        
        num_bins = self.num_data / binsize
        if self.num_data % binsize > 0:
            num_bins += 1
        
        if not os.path.isdir("pyQCDcache"):
            os.makedirs("pyQCDcache")
            
        data_sum = self._get_bin(binsize, 0)
        for i in xrange(1, num_bins):
            data_sum += self._get_bin(binsize, i)
        
        for i in xrange(num_bins):            
            bins = [j for j in xrange(num_bins) if j != i]
            
            new_datum = (data_sum - self._get_bin(binsize, i)) / (num_bins - 1)
            
            jackknife_filename = "pyQCDcache/{}_jackknife_binsize{}_{}.npz" \
              .format(self.datatype.__name__, binsize, i)
            
            new_datum.save(jackknife_filename)
                    
        self.jackknifes_cached = True          
                    
    
    def jackknife(self, func, binsize=1, args=[], use_cache=True):
        """Performs a jackknifed measurement on the dataset using the
        supplied function
        
        :param func: The measurement function
        :type func: :class:`function`
        :param binsize: The bin size used when binning
        :type binsize: :class:`int`
        :param args: The arguments required by the supplied function
        :type args: :class:`list`
        :param use_cache: Determines whether cached jackknife copies are used.
        :type use_cache: :class:`bool`
        """
        
        if binsize < 1:
            raise ValueError("Supplied bin size {} is less than 1"
                             .format(binsize))
        
        num_bins = self.num_data / binsize
        if self.num_data % binsize > 0:
            num_bins += 1
            
        out = []
            
        if use_cache:            
            if not self.jackknifes_cached:
                self.generate_jackknife_cache(binsize)
            
            for i in xrange(num_bins):
            
                jackknife_filename = "pyQCDcache/{}_jackknife_binsize{}_{}.npz" \
                  .format(self.datatype.__name__, binsize, i)
                    
                jackknife_datum = self.datatype.load(jackknife_filename)
            
                measurement = func(jackknife_datum, *args)
                if measurement != None:
                    out.append(measurement)
            
        else:
        
            data_sum = self._get_bin(binsize, 0)
            for i in xrange(1, num_bins):
                data_sum += self._get_bin(binsize, i)
        
            for i in xrange(num_bins):            
                bins = [j for j in xrange(num_bins) if j != i]
            
                new_datum = (data_sum - self._get_bin(binsize, i)) / (num_bins - 1)
            
                measurement = func(new_datum, *args)
                if measurement != None:
                    out.append(measurement)
            
        return DataSet._mean(out), DataSet._std_jackknife(out)
    
    @classmethod
    def load(self, filename):
        """Load an existing data set from the supplied zip archive
        
        :param filename: The file containing the dataset
        :type filename: :class:`str`
        :returns: :class:`DataSet`
        """
        
        storage_mode = zipfile.ZIP_DEFLATED
        compress = True
        
        try:
            zfile = zipfile.ZipFile(filename, 'r', storage_mode, True)
        except RuntimeError:
            storage_mode = zipfile.ZIP_STORED
            zfile = zipfile.ZipFile(filename, 'r', storage_mode, False)
            compress = False
        
        zfile.extract("type")
        
        typefile = open("type", 'r')
        datatype = cPickle.load(typefile)
        typefile.close()
        os.unlink("type")
        
        out = DataSet(datatype, "000.zip", compress)
        out.filename = filename
        os.unlink("000.zip")
        
        data = [int(fname[len(datatype.__name__):-4])
                for fname in zfile.namelist()
                if fname.startswith(datatype.__name__) and fname.find("jackknife") < 0]
        
        if len(data) > 0:
            out.num_data = max(data) + 1
        
        return out
    
    def _get_bin(self, binsize, binnum):
        """Average the binsize data in binnum"""
        
        out = self.get_datum(binsize * binnum)
        
        first_datum = binsize * binnum + 1
        last_datum = binsize * (binnum + 1)
        
        if last_datum > self.num_data:
            last_datum = self.num_data
        
        for i in xrange(first_datum, last_datum):
            out += self.get_datum(i)
            
        return out / binsize

    @staticmethod
    def _add_measurements(a, b):
        """Adds two measurements (used for dictionaries etc)"""
        
        if type(a) == tuple:
            a = list(a)
        if type(b) == tuple:
            b = list(b)
        
        if type(a) == list and type(b) == list:
            return [DataSet._add_measurements(x, y) for x, y in zip(a, b)]
        elif type(a) == dict and type(b) == dict:
            return DataSet._add_measurements(a, b.values())
        elif type(a) == dict and type(b) == list:
            return dict(zip(a.keys(), DataSet._add_measurements(a.values(), b)))
        elif type(a) == list and type(b) == dict:
            return DataSet._add_measurements(b, a)
        elif (type(a) == int or type(a) == float or type(a) == np.float64 \
          or type(a) == np.ndarray) \
          and (type(b) == int or type(b) == float or type(b) == np.float64 \
          or type(b) == np.ndarray):
            return a + b
        else:
            raise TypeError("Supplied types {} and {} cannot be summed"
                            .format(type(a), type(b)))

    @staticmethod
    def _sub_measurements(a, b):
        """Adds two measurements (used for dictionaries etc)"""
        
        if type(a) == tuple:
            a = list(a)
        if type(b) == tuple:
            b = list(b)
        
        if type(a) == list and type(b) == list:
            return [DataSet._sub_measurements(x, y) for x, y in zip(a, b)]
        elif type(a) == dict and type(b) == dict:
            return DataSet._sub_measurements(a, b.values())
        elif type(a) == dict and type(b) == list:
            return dict(zip(a.keys(), DataSet._sub_measurements(a.values(), b)))
        elif type(a) == list and type(b) == dict:
            return DataSet._sub_measurements(b, a)
        elif (type(a) == int or type(a) == float or type(a) == np.float64 \
          or type(a) == np.ndarray) \
          and (type(b) == int or type(b) == float or type(b) == np.float64 \
          or type(b) == np.ndarray):
            return a - b
        else:
            raise TypeError("Supplied types {} and {} cannot be summed"
                            .format(type(a), type(b)))

    @staticmethod
    def _mul_measurements(a, b):
        """Adds two measurements (used for dictionaries etc)"""
        
        if type(a) == tuple:
            a = list(a)
        if type(b) == tuple:
            b = list(b)
        
        if type(a) == list and type(b) == list:
            return [DataSet._mul_measurements(x, y) for x, y in zip(a, b)]
        elif type(a) == dict and type(b) == dict:
            return DataSet._mul_measurements(a, b.values())
        elif type(a) == dict and type(b) == list:
            return dict(zip(a.keys(), DataSet._mul_measurements(a.values(), b)))
        elif type(a) == list and type(b) == dict:
            return DataSet._mul_measurements(b, a)
        elif (type(a) == int or type(a) == float or type(a) == np.float64 \
          or type(a) == np.ndarray) \
          and (type(b) == int or type(b) == float or type(b) == np.float64 \
          or type(b) == np.ndarray):
            return a * b
        else:
            raise TypeError("Supplied types {} and {} cannot be summed"
                            .format(type(a), type(b)))
            
    @staticmethod
    def _div_measurements(a, div):
        """Divides a measurement by a scalar value"""
        
        if type(div) != float and type(div) != int:
            raise TypeError("Unsupported divisor of type {}".format(type(div)))
        
        if type(a) == list or type(a) == tuple:
            return [DataSet._div_measurements(x, div) for x in a]
        
        if type(a) == dict:
            return dict(zip(a.keys(), DataSet._div_measurements(a.values(),
                                                                div)))
        
        if type(a) == float or type(a) == int or type(a) == np.float64 \
          or type(a) == np.ndarray:
            return a / div
            
    @staticmethod
    def _sqrt_measurements(a):
        """Divides a measurement by a scalar value"""
        
        if type(a) == list or type(a) == tuple:
            return [DataSet._sqrt_measurements(x) for x in a]
        
        if type(a) == dict:
            return dict(zip(a.keys(), DataSet._sqrt_measurements(a.values())))
        
        if type(a) == float or type(a) == int or type(a) == np.float64 \
          or type(a) == np.ndarray:
            return np.sqrt(a)
        
    @staticmethod
    def _mean(data):
        """Calculates the mean of the supplied list of measurements"""
        
        if type(data) == list:
            out = data[0]
            
            for datum in data[1:]:
                out = DataSet._add_measurements(out, datum)
                
            out = DataSet._div_measurements(out, len(data))
            
            return out
        
        if type(data) == np.ndarray:
            return np.mean(data, axis=0)

    @staticmethod
    def _std(data):
        """Calculates the standard deviation of the supplied list of
        measurements"""
        
        if type(data) == list:
            mean = DataSet._mean(data)
            
            diff = DataSet._sub_measurements(data[0], mean)
            out = DataSet._mul_measurements(diff, diff)
            
            for datum in data[1:]:
                diff = DataSet._sub_measurements(datum, mean)
                square = DataSet._mul_measurements(diff, diff)
                out = DataSet._add_measurements(out, square)
                
            return DataSet._sqrt_measurements(DataSet \
                                              ._div_measurements(out, len(data)))
        
        if type(data) == np.ndarray:
            return np.std(data, axis=0)

    @staticmethod
    def _std_jackknife(data):
        """Calculates the standard deviation of the supplied list of
        measurements for the case of the jackknife"""
        
        if type(data) == list:
            mean = DataSet._mean(data)
            
            diff = DataSet._sub_measurements(data[0], mean)
            out = DataSet._mul_measurements(diff, diff)
            
            for datum in data[1:]:
                diff = DataSet._sub_measurements(datum, mean)
                square = DataSet._mul_measurements(diff, diff)
                out = DataSet._add_measurements(out, square)
                
            div = float(len(data)) / (len(data) - 1)
                
            return DataSet._sqrt_measurements(DataSet._div_measurements(out, div))
        
        if type(data) == np.ndarray:
            return np.std(data, axis=0)

    def __getitem__(self, index):
        """Square brackets overload"""
        return self.get_datum(index)
