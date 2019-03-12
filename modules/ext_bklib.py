###############################
#       Color Bar             #
###############################

# color bar ref: http://stackoverflow.com/questions/32614953/can-i-plot-a-colorbar-for-a-bokeh-heatmap
# seaborn color palette: https://stanford.edu/~mwaskom/software/seaborn/tutorial/color_palettes.html
# covert seaborn color palette to hex: http://stackoverflow.com/questions/33395638/python-sns-color-palette-output-to-hex-number-for-bokeh
# right y axis ref to twin axes: http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#twin-axes

from bokeh.plotting import figure
from bokeh.models import Range1d, LinearAxis
import seaborn as sns

def generate_colorbar( palette, low = 0, high = 1, plot_height = 400, plot_width = 80, orientation = 'v'):
    y = np.linspace( low, high,len(palette))
    dy = y[1]-y[0]
    if orientation.lower()=='v':
        fig = figure( x_range = [0, 1], y_range = [low, high], width = plot_width, height = plot_height )
        fig.toolbar_location='left'
        fig.axis.visible = False
        fig.extra_y_ranges = { 'raxis': Range1d( start = low, end = high )}
        fig.rect( x = 0.5, y = y, color=palette, width=1, height = dy )
        fig.add_layout( LinearAxis( y_range_name = 'raxis', major_label_text_font_size = '10pt' ), 'right' )
    elif orientation.lower()=='h':
        fig = figure( y_range = [0, 1], x_range = [low, high], plot_width = plot_width, plot_height=plot_height )
        fig.toolbar_location='above'
        fig.yaxis.visible = False
        fig.rect(x=y, y=0.5, color=palette, width=dy, height = 1)
    return fig

###############################
#       Polar Plot            #
###############################

# bokeh single polar plot ref: https://github.com/GCBallesteros/Bokeh_Examples/blob/master/polar.py
# bokeh 2 polar plot ref: https://github.com/GCBallesteros/Bokeh_Examples/blob/master/polar_fight.py
# hovertools: http://bokeh.pydata.org/en/latest/docs/user_guide/tools.html

import numpy as np
import math
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool

def polar( phi, r, values = None, plot_height = 400, plot_width = 400, palette = 'orange', palette_max = 1, palette_min = 0, hover_tool = False ):
    min_angle = 0
    max_angle = np.pi/2
    max_radius, r_interval = 90, 15
    max_phi, phi_interval = 90, 15

    # Coordinates in cartesian coordinates normalized
    x = r * np.cos(phi)
    y = r * np.sin(phi)

    # Create the figure
    if hover_tool:
        source = ColumnDataSource(data=dict( x = x, y = y, values = values ))
        hover = HoverTool( tooltips=[("", "@values")])
        tools = "pan,wheel_zoom,reset,save,box_select"
        p = figure( plot_width=plot_width, plot_height=plot_height,
                   tools = [hover, tools],
                   x_range=( -12, 97 ), y_range=( -12, 97))
    else:
        p = figure( plot_width=plot_width, plot_height=plot_height, x_range=( -12, 97 ), y_range=( -12, 97))
    p.axis.visible = False
    p.grid.grid_line_color = None
    
    # Plot the line and set ranges and eliminate the cartesian grid
    pal_size = len(palette)
    if pal_size > 1 and values:
        #val_pal = [ palette[int(v*pal_size)] for v in values ]
        val_interval = ( palette_max - palette_min ) / pal_size
        pal_index = [ ( v - palette_min ) / val_interval for v in values ]
        pal_index = [ pal_size - 1 if v >= pal_size else 0 if v < 0 else v for v in pal_index ]
        val_pal = [ palette[math.ceil(ind)] for ind in pal_index ]
        if hover_tool:
            p.scatter( 'x', 'y', size=15, radius = 3, line_color = None, fill_color = val_pal, source = source )
        else: p.scatter( x, y, size=15, radius = 3, line_color = None, fill_color = val_pal )
    else:
        p.scatter( x, y, size=15, radius = 3, line_color = None, fill_color = palette )

    # Draw the radial coordinates grid
    radius = list( range( 0, max_radius+1, r_interval ))
    zeros = np.zeros( len( radius ))
    p.annular_wedge(zeros, zeros, zeros, radius, 0, np.pi/2,
                    fill_color=None, line_color="gray",
                    line_dash="4 4", line_width=0.5)
    p.annular_wedge([0.0], [0.0], [0.], [max_radius], 0, np.pi/2,
                    fill_color=None, line_color="#37435E", line_width=1.5)

    # Radial Labels
    x_labels = -3.5
    y_labels = np.linspace(0, max_radius, len( radius ))
    number_labels = ["%.0f°" % s for s in y_labels ]
    # - y label
    p.text( x_labels, y_labels, number_labels,
            angle=np.zeros( int( max_radius/r_interval )),
            text_font_size="11pt", text_align="right", text_baseline="middle",
            text_color="gray")
    # - x label
    p.text( [ y+3.5 for y in y_labels ], x_labels-2, number_labels,
            angle=np.zeros( int( max_radius/r_interval )),
            text_font_size="11pt", text_align="right", text_baseline="middle",
            text_color="gray")

    #Draw angular grid
    phi_angles = list( range( 0, max_phi+1, phi_interval ) )
    n_spokes = len( phi_angles )
    angles_spokes = np.linspace( min_angle, max_angle, n_spokes)
    p.ray( np.zeros(n_spokes), np.zeros(n_spokes), np.ones(n_spokes)*max_radius,
            angles_spokes,
            line_color="gray", line_width=0.5, line_dash="4 4")

    # Angle Labels
    x_labels = max_radius * np.cos(angles_spokes)
    y_labels = max_radius * np.sin(angles_spokes)
    p.text(x_labels, y_labels, [ str(a)+'°' for a in phi_angles ],
         angle=-np.pi/2+angles_spokes,
         text_font_size="11pt", text_align="center", text_baseline="bottom",
         text_color="gray")

    return p

