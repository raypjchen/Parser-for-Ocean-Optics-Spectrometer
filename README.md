# Spectrum Parser for Ocean Optics Spectrometer

This parser strips, smooths, normalizes, and accumulates the spectrum of highest intensity from measured data. The data analysis supports to calculate spectral shift coefficient (S) and apparent Huang–Rhys factor (apparent H-R factor). The results are exported as Microsoft Excel file (.xlsx) and plot on Jupyter Notebook.

### Getting Started

The spectrum parser is written in Python 3 with numpy, pandas, seaborn, bokeh, and [Jupyter Notebook](https://jupyter.org/). If you use [Anaconda](https://www.anaconda.com/distribution/) distribution of python, the following commend will install required modules for the program.

```
$ conda install numpy pandas seaborn bokeh jupyter
```
open Jupyter Notebook on commend line:

```
$ jupyter notebook
```

walk into the the directory that contains the downloaded parser. A Jupyter Notebook, PLSpecParserOceanOptics.ipynb, is in the directory. Click the notebook file to open. 

## Run the Example

A demos of single data set and multiple data sets. 

### Configure Bokeh Output State

All the graphs are plotted with Bokeh plotting module, so the program configures the default output state to generate output in notebook cells on the top of notebook. 

```
from bokeh.io import output_notebook
output_notebook()
```

### Single Data Set

Single data set is that a result directory has multiple data points of measurement. The hierarchy of data set folders is in the example below:

```
- data_set_directory
   |- a
   |- a.dat
   |- b
   |- b.dat
```

The 2nd notebook cell has 2 parts including input settings and execution. 

#### Path of Directories
* Background spectrum

```
bg_path = 'directory of background path'
```

* Sample's PL spectra

```
pl_path = 'directory of PL path'
```

#### Wavelength Range of PL Spectrum

```
WL_range = [minimum, maximum]
```

#### Smoothing Window
The type of smoothing window is triang for Pandas of DataFrame. 

```
smo_win = a_number_larger_than_one
```

#### Settings of Spectral Shift Coefficient (S) and Apparent Huang–Rhys Factor 
The spectral coefficient and apparent H-R factor are not required for inputs.

* [Spectral Coefficient](https://doi.org/10.1103/PhysRevB.74.085209) 

```
WL_SSC_split = main_peak_wavelength
```

* Apparent [H-R factor](https://doi.org/10.1016/0022-3697(65)90217-9): a quick estimation of H-R factor without curve fitting

```
aHR_range = [main_min, main_max, shoulder_min, shoulder_max] #set wavelength range of main peak and shoulder
```

### Multiple Data Sets
The idea of multiple data sets is that a result directory contains multiple measurement. The parser can do batch processing with one function. The hierarchy of data set folders is in the example below:

```
- data_sets_directory
   |- first_data_set
       |- a1
       |- a1.dat
       |- b1
       |- b1.dat
   |- second_data_set
       |- a2
       |- a2.dat
       |- b2
       |- b2.dat
```

The 3rd notebook cell is a demo of multiple data sets. The input settings of multiple data set are the same as single data set.

## Authors

* **Ray Po-Jui Chen** - *Initial work* - [Ray PJ Chen](https://github.com/raypjchen)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
