
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy
import cartopy.feature as cfeature
import numpy as np
import re
import sys
import argparse

#Set high-res coastline
coastline = cfeature.NaturalEarthFeature(   category='physical',
                                              name='land',
                                              scale='50m',
                                              facecolor=cfeature.COLORS['land'])

#Set high-res borders
countries = cfeature.NaturalEarthFeature(   category='cultural',
                                              name='admin_0_boundary_lines_land',
                                              scale='50m',
                                              facecolor='none')

# Dictionary with colors, linestyles and linewidths for the domain
resolutions={
'01':['k','--',3],
'02':['b','--',3],
'03':['r','--',3],
'04':['m','--',3],
'05':['y','--',3],
'06':['0.5','--',3],
'07':['c','--',3],
'08':['k','-',2],
'09':['b','-',2],
'10':['r','-',2],
'11':['m','-',2],
'12':['y','-',2],
'13':['0.5','-',2],
'14':['c','-',2],
'15':['k',':',2],
'16':['b',':',2],
'17':['r',':',2],
'18':['m',':',2],
'19':['y',':',2],
'20':['0.5',':',2],
'21':['c',':',2],
#### Add more if needed
}

##########################################################################
#                                  MAIN PROGRAM                          #
##########################################################################
def main(arg):
    """ Reads in rose-suite.conf to find the grid info (centre, number of
    points, delta, offset and if it is a rotated grid, then plots all
    domains and adjust the plot to the biggest domain

    Arguments:
         arg    -- Location of the rose-suite.conf file

    """
    #Get argument (rose-suite.conf path)
    parser = argparse.ArgumentParser()
    parser.add_argument('roseconf_file')
    args = parser.parse_args()

    #Do plotting
    do_plot(args.roseconf_file)

##########################################################################
#                     AUX PROGRAMS                                       #
##########################################################################

# do_plot
#################
def do_plot(roseconf_file):
    """ Set ups figure for plots and call functions to get domain (get_domain)
    get name of model (get_str), plot it (plot_box) and adjust plot to
    bigger domain (set_big_plot)

       Arguments:
         roseconf_file    -- path to the rose-suite.conf file
    """
    # Set figure
    fig = plt.figure(figsize=(12,8))
    ax=plt.subplot(1,1,1, projection=cartopy.crs.PlateCarree())

    ### Get number of Resolutions
    # note: Regions not needed as it is set to 0:1
    nreg=int(get_float(roseconf_file,'rg01_nreslns')[1])

    #Loop over resolutions
    for r in range(1,nreg+1):

        #Get resolution domain
        box=get_domain(roseconf_file,r)

        #get name of the resolution
        name=get_str(roseconf_file,r)

        #Do plot
        plot_box(name,box,r)

        #Get bigger box to plot limits
        if r==1:bigger_box=box


    #Set grids and plot limits
    set_big_plot(bigger_box)

    #Add coastlines and countries
    plt.gca().add_feature(coastline)
    ax.add_feature(countries)

    #Add legend
    plt.legend(loc='best',fontsize=16)

    #Save plot
    plt.show()
    plt.close()


##########################################################################
#                     AUX PROGRAMS                                       #
##########################################################################

# get_domain
#################
def get_domain(roseconf_file,r):
    """ Reads in rose-suite.conf to find for a domain r its centre,
    delta, No of points, offset and if it is a rotated grid.
    Then computes the domain's E,W,N,S coords

       Arguments:
         roseconf_file    -- path to the rose-suite.conf file
         r     -- integer looping over No of domains
       Returns:
         Box with domain coordinates
    """
    #Get domain details from rose-suite.conf
    centre=get_float(roseconf_file,'rg01_centre')[1:3]
    delta=get_float(roseconf_file,'rg01_rs'+str(r).zfill(2)+'_delta')[2:4]
    npts=get_float(roseconf_file,'rg01_rs'+str(r).zfill(2)+'_npts')[2:4]
    offset=get_float(roseconf_file,'rg01_rs'+str(r).zfill(2)+'_offset')[2:4]
    do_rotate=get_bol(roseconf_file,'rg01_rot_grid')

    pole=rot_pole(centre,do_rotate)


    # Get corners of the box as Centre + ( Npts x Delta + 1)/2 + offset
    S_dom=float(centre[0])-(float(npts[0])*float(delta[0]))/2.+float(offset[0])
    N_dom=float(centre[0])+(float(npts[0])*float(delta[0]))/2.+float(offset[0])

    E_dom=float(centre[1])-(float(npts[1])*float(delta[1]))/2.+float(offset[1])
    W_dom=float(centre[1])+(float(npts[1])*float(delta[1]))/2.+float(offset[1])

    # Make box
    box=[E_dom,S_dom,W_dom,N_dom]

    return box

# get_float
#################
def get_float(roseconf_file,text):
  """ Finds in rose-suite.conf the float value of a given variable name
    Using re.findall

       Arguments:
         roseconf_file    -- path to the rose-suite.conf file
         text             -- a string containing the variable name
       Returns:
         Value of the float
  """

  line_out=find_line(roseconf_file,text)

  #Strip numbers out
  out=re.findall(r'-?\d+\.?\d*',line_out)

  return out

# get_str
#################
def get_str(roseconf_file,r):
    """ Finds in rose-suite.conf the name of the domain given by integer r

       Arguments:
         roseconf_file    -- path to the rose-suite.conf file
         r                -- Integer of the domain number
       Returns:
         Name of the domain
    """

    line_out=find_line(roseconf_file,'rg01_rs'+str(r).zfill(2)+'_name')

    #Get name from full line
    name=line_out[line_out.index('"')+1:line_out.rindex('"')]

    return name

# get_bol
#################
def get_bol(roseconf_file,text):
    """ Finds in rose-suite.conf the boolean value of a given variable name
    Using re.findall

       Arguments:
         roseconf_file    -- path to the rose-suite.conf file
         text             -- a string containing the variable name
       Returns:
         The value (T of F) of the variable
    """

    line_out=find_line(roseconf_file,text)

    #Get name from full line
    name=line_out[line_out.index('=')+1:]

    #Remove trailing line
    if name.endswith("\n"): name=name[:-1]

    #Convert to Boolean
    if name.upper()=='TRUE':
        flag=True
    elif name.upper()=='FALSE':
        flag=False
    else:
        sys.exit(text+' != to False or True')

    return flag


# find_line
#################
def find_line(roseconf_file,text):
    """ Finds a given string in the rose-suite.conf file

       Arguments:
         roseconf_file    -- path to the rose-suite.conf file
         text             -- a string containing the variable name
       Returns:
         The line where the string is found
    """
    datafile = file(roseconf_file)
    found = False
    for line in datafile:
      if text in line:
          found = True
          line_out=line
          break

    return line_out

# rot_pole
#################
def rot_pole(centre, do_rotate):
    """Computes the North pole coordinates for a model domain.

       Arguments:
         centre -- coordinates (latitude, longitude) of the centre of
                   the domain
       Keyword arguments:
         do_rotate -- if this is true a coordinate system with a rotated
                      pole will be adopted
       Returns:
         The (latitude, longitude) coordinates of the North pole of the
         domain with the specified centre.
    """
    if do_rotate:
        if float(centre[0]) >= 0.0:
	    pole_lat = 90.0 - float(centre[0])
	    pole_lon = float(centre[1]) + 180.0
	    if pole_lon >= 360.0:
	        pole_lon = pole_lon - 360.0
	    if pole_lon < 0.0:
	        pole_lon = pole_lon + 360.0
	else:
	    pole_lat = 90.0 + float(centre[0])
	    pole_lon = float(centre[1])
	    if pole_lon >= 360.0:
	        pole_lon = pole_lon - 360.0
	    if pole_lon < 0.0:
	        pole_lon = pole_lon + 360.0
    else:
        pole_lat = 90.0
	pole_lon = 180.0

    return (pole_lat, pole_lon)

# plot_box
#################
def plot_box(name,box,r):
    """Plots the domain given

       Arguments:
         name -- Name of the domain for legend
         box  -- list with coordinates of the domain
         r    -- Looping Integer with the domain's number
    """
    rtag=str(r).zfill(2)

    # Plot box [color,ls,lw]
    plt.plot([box[0],box[0]],[box[1],box[3]],resolutions[rtag][0],ls=resolutions[rtag][1],lw=resolutions[rtag][2],label=name)
    plt.plot([box[2],box[2]],[box[1],box[3]],resolutions[rtag][0],ls=resolutions[rtag][1],lw=resolutions[rtag][2])
    plt.plot([box[0],box[2]],[box[1],box[1]],resolutions[rtag][0],ls=resolutions[rtag][1],lw=resolutions[rtag][2])
    plt.plot([box[0],box[2]],[box[3],box[3]],resolutions[rtag][0],ls=resolutions[rtag][1],lw=resolutions[rtag][2])

#  set_big_plot
#################

def set_big_plot(box):
    """Sets domains of the plot to the biggest domain + adjust the grid to the
       size of domain

       Arguments:
         box  -- list with coordinates of the domain
    """

    ## Could add functionality to finer edges (<1 deg) for very high resolution
    E=np.floor(box[0])
    S=np.floor(box[1])
    W=np.ceil(box[2])
    N=np.ceil(box[3])

    # Plot grid lines

    gl=plt.gca().gridlines(draw_labels=True,linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False

    # Customize lat-lon limits
    plt.xlim([E,W])
    plt.ylim([S,N])

#                     END OF PROGRAM                                     #
##########################################################################
if __name__ == '__main__':
    main(sys.argv[1:])
