import numpy as np
import seaborn as sns

def cw_color( color_cnt ):
    return sns.color_palette("coolwarm", color_cnt ).as_hex()

def qcolor10( color_cnt ):
    return sns.color_palette("hls", color_cnt ).as_hex()

def qcolor20( color_cnt ):
    cpalette = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
    return cpalette * int( color_cnt / 20 ) + cpalette[: color_cnt%20]

def qcolor30( color_cnt ):
    cpalette = ['#fb8072', '#dbdb8d', '#bebada', '#8dd3c7', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5', '#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#d7191c', '#fdae61', '#ffffbf', '#abd9e9', '#2c7bb6', '#008837', '#7b3294', '#a6dba0' ]
    return cpalette * int( color_cnt / 30 ) + cpalette[: color_cnt%30]

def ran_color( color_cnt ):
    # generate colors code for plotting
    x = np.random.random( size = color_cnt ) * 100
    y = np.random.random( size = color_cnt ) * 100
    return [ "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip( 50+2*x, 30+2*y ) ]

def ran_color_times( color_cnt, times ):
    colors = ran_color( color_cnt )
    return [ c for c in colors for i in range(times) ]
