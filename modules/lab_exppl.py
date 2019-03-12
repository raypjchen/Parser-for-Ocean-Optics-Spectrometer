import pandas as pd
import os, sys, warnings
import numpy as np

from bokeh.models import ColumnDataSource, Legend
from bokeh.plotting import figure, gridplot, show

from fpathlib import getDatDirPath
from colorlib import qcolor20

class ExpPL:
    def __init__( self, WL_setup = [0,0,0], bg_path = None, fg_save = True, fg_legend = True, fg_plot = True, fg_ang = True, pSSC_range = [0.3, 0.7], aHR_range = [550, 570, 590, 610], smo_win = 5 ):
        # initialize: min wavelength (WL_min), max wavelength (WL_max), peak wavelength (WL_peak)
        self.WL_min, self.WL_max, self.WL_peak = WL_setup
        self.init_check()
        # path of background spectra
        self.bg_path = bg_path
        # angular analysis
        self.fg_ang = fg_ang
        # flag of saving spectrum
        self.fg_save = fg_save
        # - range of Spectral Shift Coefficient
        self.pSSC_range = pSSC_range
        # - range of apparent H-R factor
        self.aHR_range = aHR_range
        # - smooth window of data frame
        self.smo_win = smo_win
        # == plotting ==
        # - flag
        self.fg_plot = fg_plot
        # flag of display legend in graph
        self.fg_legend = fg_legend

    def init_check( self ):
        if self.WL_min == self.WL_max:
            print( 'self.WL_min == self.WL_max', str( self.WL_min ))
        elif self.WL_min > self.WL_max:
            print( 'self.WL_min ({}) > self.WL_max ({})'.format( str( self.WL_min ), str( self.WL_max )))

    def find_index_MaxValList( self, sum_val ):
        """find highest intensity spectra in summary list and return its index of list"""
        max_ind = -1
        max_tmp = 0
        for i, values in enumerate( sum_val ):
            if ( max( values ) > max_tmp ):
                max_ind = i
                max_tmp = max( values )
        return max_ind

    def interpolate_spec( self, spec ):
        # interpolate WL[self.WL_min-1:self.WL_max]
        # - redinx: insert index to data frame and the intensity remains Nan
        spec_ix = list( range( self.WL_min, self.WL_max + 1 ))
        specRI = spec.reindex( index = pd.Index( sorted( set( spec_ix + list( spec.index )))))
        # - linear interpoloate based on the wavelength
        specRI.interpolate( method = 'index', inplace = True )
        # - spectrum: range[self.WL_min, 1, self.WL_max]
        spec_strip = specRI.ix[spec_ix]
        spec_strip.index.rename( 'Wavelength', inplace = True )
        return spec_strip

    def calSpecShiftCoef( self, spec ):
        # Spectrum Shift Coefficient
        spec_sp = spec['Intensity'][:self.WL_peak-self.WL_min+1].tolist()
        spec_pe = spec['Intensity'][self.WL_peak-self.WL_min+1:].tolist()
        # S = [I(>WL_peak) - I(<WL_peak)] / I(WL_min-WL_max)
        spec_shift_coef = ( (sum(spec_pe) - sum(spec_sp)) / spec['Intensity'].sum())
        return spec_shift_coef

    def calHR_factor( self, spec ):
        # Apparent H-R factor
        main = spec['Intensity'][self.aHR_range[0]-self.WL_min:self.aHR_range[1]-self.WL_min].tolist()
        shoulder = spec['Intensity'][self.aHR_range[2]-self.WL_min:self.aHR_range[3]-self.WL_min].tolist()
        # H-R factor = max(soulder_peak) / max(main_peak)
        return max( shoulder ) / max( main )

    def read_dat_path( self, par_dir ):
        # read summary file
        # - path: summary file
        path = [ ( d + '.dat', d ) for d in getDatDirPath( par_dir ) if os.path.isfile( d + '.dat' )]
        if not path: print('No Summary File in', par_dir )
        #print('path:', path )

        spec_dat_path = []
        for fpath, dir_path in path:
            # - open & read summary file: find index of highest intesnity spectra
            with open( fpath, 'r' ) as infile:
                summary = [ s.split() for s in infile.readlines() ]
                if len( summary ) == 1: 
                    print('\tWARNING: No Spectra Data in Summary File.\n\tSummary File:', fpath, '\n\tFolder:', dir_path )
                    continue
                sum_val = [ [ float(ss) for ss in s ][1:] for s in summary[1:] ]
                # find index of highest intesnity spectra
                max_ind = self.find_index_MaxValList( sum_val )
                # set file path of highest intensity spectra
                spec_dat_path.append( os.path.join( dir_path, summary[max_ind+1][0] + '.dat' ))
        #print( 'dat path:', spec_dat_path)
        return spec_dat_path

    def spec_smooth( self, spec ):
        return spec.rolling( window = self.smo_win, min_periods = 1, center = True, win_type = 'triang', closed = 'both' ).mean()
    
    def read_spectra( self, infile, bg_spec = None, fg_smooth = True ):
        spec = pd.read_table( infile, header = None, usecols = [1, 2], dtype = np.float64, index_col = 0 )
        # substract background if background path exist (self.bg_path)
        spec = self.sub_background( spec, bg_spec )
        # smooth
        if fg_smooth:
            spec = self.spec_smooth( spec )
            # strip laser light
            spec = spec[ self.WL_min-1 : self.WL_max+1 ]
        spec.columns = ['Intensity']
        return spec

    def read_raw_data( self, fpath, bg_spec = None, fg_smooth = True ):
        print( 'dat:', '/'.join( fpath.split( os.sep )[-2:] ))
        with open( fpath, 'r' ) as infile:
            spec = self.read_spectra( infile, bg_spec = bg_spec, fg_smooth = fg_smooth )
            # interpolated spectra WL[WL_min-WL_max, step = 1]
            spec = self.interpolate_spec( spec )
            spec.where( spec.values >= 0, other = 0, inplace = True )
        return spec

    def read_background( self ):
        if self.bg_path:
            print('== READ BACKGROUND ==')
            bgpath = self.read_dat_path( self.bg_path )[0]
            print( 'dat:', '/'.join( bgpath.split( os.sep )[-2:] ))
            with open( bgpath, 'r' ) as infile:
                bg = self.read_spectra( infile, fg_smooth = False )
                bg.where( bg.values >= 0, other = 0, inplace = True )
            print('=====================')
            return bg
        return None

    def sub_background( self, spec, bg_spec ):
        try:
            spec = spec.sub( bg_spec['Intensity'].values, axis = 0 )
            return spec.where( spec.values >= 0, other = 0 )
        except TypeError:
            return spec

    def read_data( self, spec_dat_path, bg_spec ):
        # read spectra & strip the redundant wavelength
        Spec, NorSpec, IntSpec, spec_shift_coef, aHR_factor = [[], [], [], [], []]
        for fpath in spec_dat_path:
            # read spectra
            spec = self.read_raw_data( fpath, bg_spec )
            Spec.append( spec )
            # normalized spectra
            NorSpec.append( spec / spec.max())
            # integral intensity
            IntSpec.append( spec['Intensity'].sum())
            # calculate spectra shift coefficient
            spec_shift_coef.append( self.calSpecShiftCoef( spec ))
            # calculate apparent H-R factor
            aHR_factor.append( self.calHR_factor( spec ))
        return Spec, NorSpec, IntSpec, spec_shift_coef, aHR_factor

    def sort_phi( self, indata ):
        data = pd.DataFrame( indata, copy=True  )
        data.sort_values( ['phi', 'theta'], inplace = True )
        return data

    def add_angle( self, data ):
        angle = [ aa for a in data.index.tolist() for aa in a.split() if 't' in aa and 'p' in aa ]
        if angle:
            data['theta'] = [ float( a[1:3] ) for a in angle ]
            data['phi_rad'], data['phi'] = [ float( a[4:6] )*np.pi/180 for a in angle ], [ float( a[4:6] ) for a in angle ]
        else:
            data['theta'] = [ float(aa[1:]) for a in data.index.tolist() for aa in a.split() if 't' in aa ]
            data['phi'] = [ float(aa[1:]) for a in data.index.tolist() for aa in a.split() if 'p' in aa ]
            data['phi_rad'] = [ a * np.pi / 180 for a in data['phi']]
        return data

    def get_save_path( self, sp_par_dir ):
        return os.path.join( '', *[ *sp_par_dir[0:-2], sp_par_dir[-2] + '.xlsx'] )

    def save_spectrum( self, SpecAll, NorSpecAll, IntSpec, spec_shift_coef, aHR_factor, par_dir ):
        # Save results as XLSX file:
        # - setup file path of results
        sp_par_dir = par_dir.split( os.sep )
        export_fname = self.get_save_path( sp_par_dir )
        print( 'Exported Spectrum:', export_fname )
        if self.fg_ang:
            # - convert spec_shift_coef to pandas.DataFrame
            SpecShiftCoef = self.add_angle( pd.DataFrame( {'SpecShiftCoef': spec_shift_coef }, index = SpecAll.columns ))
            SPT_SSC = self.sort_phi( SpecShiftCoef )
            # - convert aHR_factor to pandas.DataFrame
            aHR_Factor = self.add_angle( pd.DataFrame( {'aHR': aHR_factor }, index = SpecAll.columns ))
            SPT_HR = self.sort_phi( aHR_Factor )
            # - convert IntSpec to pandas.DataFrame
            IntegralSpec = self.add_angle( pd.DataFrame( {'IntSpec': IntSpec }, index = SpecAll.columns ))
            SPT_IS = self.sort_phi( IntegralSpec )
        else:
            # - convert spec_shift_coef to pandas.DataFrame
            SpecShiftCoef = pd.DataFrame( {'SpecShiftCoef': spec_shift_coef }, index = SpecAll.columns )
            # - convert aHR_factor to pandas.DataFrame
            aHR_Factor = pd.DataFrame( {'aHR': aHR_factor }, index = SpecAll.columns )
            # - convert IntSpec to pandas.DataFrame
            IntegralSpec = pd.DataFrame( {'IntSpec': IntSpec }, index = SpecAll.columns )

        with pd.ExcelWriter( export_fname ) as export_xlsx:
            SpecAll.to_excel( export_xlsx, sheet_name = 'Spectrum' )
            NorSpecAll.to_excel( export_xlsx, sheet_name = 'NormalizedSpec' )
            SpecShiftCoef.to_excel( export_xlsx, sheet_name = 'SpecShiftCoef' )
            aHR_Factor.to_excel( export_xlsx, sheet_name = 'aHR' )
            IntegralSpec.to_excel( export_xlsx, sheet_name = 'IntSpec' )
            if self.fg_ang:
                SPT_SSC.to_excel( export_xlsx, sheet_name = 'SPT_SSC' )
                SPT_HR.to_excel( export_xlsx, sheet_name = 'SPT_aHR' )
                SPT_IS.to_excel( export_xlsx, sheet_name = 'SPT_IntSpec' )
            export_xlsx.save()

    def spec_column_name( self, spec_dat_path ):
        return [ p.split( os.sep )[-2] for p in spec_dat_path ]
        
    def merge_data( self, Spec, NorSpec, IntSpec, spec_shift_coef, aHR_factor, spec_dat_path ):
        # concatenate dataframe of spectrum
        # - create column name for raw and normalized intensity
        specColName = self.spec_column_name( spec_dat_path )
        NorSpecColName = [ 'Nor ' + s for s in specColName ]
        # - joint all raw and normalized spectrum
        SpecAll = pd.concat( Spec, axis = 1 )
        NorSpecAll = pd.concat( NorSpec, axis = 1 )
        # - update column names
        SpecAll.columns = specColName
        NorSpecAll.columns = NorSpecColName

        # - joint raw & normalized spectrum
        spectrum = pd.concat( [SpecAll, NorSpecAll], axis = 1 )
        # - joint spectrum, integraled intensity, spectral shfit, apparent H-R factor
        index = [ v + self.WL_min for v in range( len( specColName ))]
        spectrum['SpecShiftCoef'] = pd.Series( spec_shift_coef, index = index )
        spectrum['IntSpec'] = pd.Series( IntSpec, index = index )
        spectrum['aHR'] = pd.Series( aHR_factor, index = index )

        # export result
        if self.fg_save:
            self.save_spectrum( SpecAll, NorSpecAll, IntSpec, spec_shift_coef, aHR_factor, os.path.dirname( spec_dat_path[0] ))

        return spectrum, specColName, NorSpecColName

    def get_processed_spec( self, spec_dat_path, bg_spec ):
        return self.merge_data( *self.read_data( spec_dat_path, bg_spec ), spec_dat_path )

    def config_plot( self, spectrum ):
        # plotting
        # - figure configuration
        plot_config = dict( plot_height = 300, toolbar_location = 'left' )
        N = int( len(spectrum.columns) / 2 )
        if N < 5: N = 5
        colors = qcolor20( N )

        # - create figure
        if not self.fg_legend: ptw = 300
        else: ptw = 550
        intensity = figure( **plot_config, plot_width = ptw, x_range = [ self.WL_min, self.WL_max], 
                            x_axis_label = 'Wavelength', y_axis_label = 'Intensity' )
        nor_intensity = figure( **plot_config, plot_width = 300, x_range = [ self.WL_min, self.WL_max], y_range = [0, 1.05], 
                            x_axis_label = 'Wavelength', y_axis_label = 'Normalized Intensity' )
        shift_coef = figure( **plot_config, plot_width = 300, x_range = [ self.WL_min-1, self.WL_min + N ], y_range = self.pSSC_range, 
                            y_axis_label = 'Shift Coefficient (/'+ str(self.WL_peak) + 'nm)' )
        integral_spec = figure( **plot_config, plot_width = ptw, x_range = [ self.WL_min-1, self.WL_min + N ], 
                            y_axis_label = 'Ingetral Spectrum' )

        # - set figure source
        source = ColumnDataSource( data = spectrum )
        return source, intensity, nor_intensity, integral_spec, shift_coef, colors

    def create_external_legend( self, specColName, rLeg ):
        legend = Legend( items = [ ( specColName[i], [rLeg[i]] ) for i in range( len(specColName))], location = ( 0, 0 ))
        legend.background_fill_alpha = 0
        legend.label_text_font_size = '6pt'
        legend.border_line_width = 0
        legend.spacing = -10
        legend.label_width = 150
        return legend

    def plot_spectrum( self, spectrum, specColName, NorSpecColName ):
        source, intensity, nor_intensity, integral_spec, shift_coef, colors = self.config_plot( spectrum )
        if self.fg_legend: rLeg = []
        for i in range( len( specColName )):
            # raw intensity
            if not self.fg_legend: intensity.line( x = 'Wavelength', y = specColName[i], color = colors[i], line_width = 2, alpha=0.6, source = source )
            else: rLeg.append( intensity.line( x = 'Wavelength', y = specColName[i], color = colors[i], line_width = 2, alpha=0.6, source = source ))
            # normalized intensity
            nor_intensity.line( x = 'Wavelength', y = NorSpecColName[i], color = colors[i], alpha=0.6, source = source )

        # spectrum shift coefficient
        integral_spec.scatter( x = 'Wavelength', y = 'IntSpec', color = colors[0], alpha=0.6, source = source )
        shift_coef.scatter( x = 'Wavelength', y = 'SpecShiftCoef', color = colors[0], alpha=0.6, source = source )
        shift_coef.scatter( x = 'Wavelength', y = 'aHR', color = colors[2], alpha=0.6, source = source )
        # legend settings
        if self.fg_legend:
            legend = self.create_external_legend( specColName, rLeg )
            intensity.add_layout( legend, 'right' )
        # make a grid & show the results
        show( gridplot([intensity, nor_intensity, integral_spec, shift_coef ], ncols=2, sizing_mode='fixed'))

        return spectrum, specColName, NorSpecColName

    def single_folder( self, dir_path ):
        spec_dat_path = self.read_dat_path( os.path.join( dir_path, '' ))
        if not spec_dat_path: sys.exit()
        bg_spec = self.read_background()
        if self.fg_plot:
            return self.plot_spectrum( *self.get_processed_spec( spec_dat_path, bg_spec ))
        else: return self.get_processed_spec( spec_dat_path, bg_spec  )

    def mutiple_folder( self, dir_path ):
        dir_path = getDatDirPath( dir_path )
        if not dir_path: sys.exit()
        bg_spec = self.read_background()
        for dpath in dir_path:
            print('#====================================================================#')
            print('Spectrum folder: ' + dpath )
            spec_dat_path = self.read_dat_path( os.path.join( dpath, '' ))
            if spec_dat_path:
                if self.fg_plot:
                    self.plot_spectrum( *self.get_processed_spec( spec_dat_path, bg_spec ))
                else: self.get_processed_spec( spec_dat_path, bg_spec  )
            else: print('No Data File')

