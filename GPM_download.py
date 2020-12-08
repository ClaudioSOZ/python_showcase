#!/usr/bin/env python

import iris
import datetime
import os
import sys
import argparse
'''
This script GPM_download runs fine in Python 3.6.8 version, it needs IRIS v2.2
library (https://scitools.org.uk/iris/docs/latest/)

The Integrated Multi-satellitE Retrievals for the Global Precipitation 
Measurements (IMERG-GPM) estimates precipitation over the majority 
of the Earth's surface. More info at https://gpm.nasa.gov/data/imerg
The script retrieves and accumulates precipitation for 
a given user defined interval, dates, product, region
and the output placed in a user defined location.
Is reads the data from a centralized location (described below)

For info about arguments run
GPM_download.py -h

How to call the script
GPM_download.py  --ini 20200101T0000Z --fin 20200102T0000Z --int 3      \
          --reg 40,-20,100,50 --prod production --dir $HOME/temp/

############ Examples of regions:

Indian Ocean:       40, -20, 100, 50
South East Asia:    88, -20, 156, 32
North Atlantic:    -30,  35,  20, 70,

############ CENTRALIZED DATA

### Met Office

At the Met Office, IMERG-GPM data is stored in the central location
/project/earthobs/PRECIPITATION/GPM/netcdf/imerg/${product}/${YEAR}/
on daily files, each containing 30 min accumulated precipitation
(48 time frames). Filenames are given as 
gpm_imerg_/${product}_${VERSION}_${DATE}.nc
Where ${product} and ${VERSION} are the satellite product and its version
respectively, ${year} and ${DATE} the
Year and date (%Y%m%d) of the day to be retrieved. 

### Non-Met Office

Please download from https://gpm.nasa.gov/taxonomy/term/1366
Note: 'production' tag for product is 'final' in this website
Needs registering

############ CHANGES NEEDED FOR NON-MET OFFICE SITES

To use outside Met Office, change gpm_path variable at L21 accordingly
and the filenames (if different) at L118.

To employ another library to load, time-average and save netcdf files 
than IRIS, like xarray or netCDF4. Change L197-203 to read the 
required temporal fields and average over time. 
Then change L238 to save output files.

Any issues contact Claudio Sanchez (claudio.sanchez@metoffice.gov.uk)
'''

################### End of user-defined variables,

# GPM version
GPM_V='V06B'

## GPM Path
path_gpm='/project/earthobs/PRECIPITATION/GPM/netcdf/imerg/'

##########################################################################
#                     MAIN PROGRAM, ITERATE THROUGH TIME                 #
##########################################################################
def main():
    '''
    This script downloads GPM-IMERG satellite rainfall product, tailored for a user-defined accumulation interval, product, 
    pre-defined region and the initial and final time to download
    '''
    # Parse command line arguments
    args = parse_args()
    
    #Check arguments
    check_args(args.interval,args.region,args.product)

    #Time iter to loop from init_time to final_time
    time_iter=args.init_time

    while time_iter <= args.final_time:
      # Define end of acc interval
      time_iter_top=time_iter + datetime.timedelta(hours=args.interval)

      print( 'Doing {:%HZ %d/%m/%Y} to {:%HZ %d/%m/%Y}'.format(time_iter,time_iter_top))
      #Get cubes
      cube=get_gpm_cubes(time_iter,args.region,args.interval,args.product)

      #Save cube
      gpm_cube_save(cube,time_iter,args.interval,args.path_out)

      #Iterate to next time
      time_iter=time_iter_top

##########################################################################

def parse_args():
  '''Parses and returns command line arguments.'''
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      description="Download GPM-IMERG Satellite rainfall product")

  # Required arguments    
  parser.add_argument("--ini",
                      type=cycletime_to_datetime,
                      help=("Initialisation time in ISO8601 "
                            "format YYYYmmddTHHMMZ"),
                      default=True,
                      dest="init_time")
  
  parser.add_argument("--fin",
                      type=cycletime_to_datetime,
                      help=("Finalization time in ISO8601 "
                            "format YYYYmmddTHHMMZ"),
                      default=True,
                      dest="final_time")

  parser.add_argument("--int",
                      type=int,
                      help=("Accumulation interval in hours"),
                      default=True,
                      dest="interval")

  parser.add_argument("--reg",
                      type=region_str_to_list,
                      help=("Region to extract in"
                            "E,S,W,N coordinates"),
                      default=True,
                      dest="region")

  parser.add_argument("--prod",
                      type=str,
                      help=("Stream, specify 'production' or 'NRTLate'"),
                      default=True,
                      dest="product")

  parser.add_argument("--dir",
                      type=str,
                      help=("Output directory, if None it will "
                            "be stored in $HOME"),
                      default=True,
                      dest="path_out")

  # Parse the arguments
  args = parser.parse_args()

  # Checking of input arguments are there 
  if not args.init_time:
      raise argparse.ArgumentTypeError("Must supply Init time in YYYYmmddTHHMMZ "
                                       "format in --ini")

  if not args.final_time:
      raise argparse.ArgumentTypeError("Must supply Final time in YYYYmmddTHHMMZ "
                                       "format in --fin")

  if not args.interval:
      raise argparse.ArgumentTypeError("Must supply acc internval in hours "
                                       "in --int arg")

  if not args.region:
      raise argparse.ArgumentTypeError("Must supply region as E,S,W,N coords")

  if not args.product:
      raise argparse.ArgumentTypeError("Must supply 'production','NRTLate' or 'NRTearly' "
                                        "in --prod argument")

  if not args.path_out:
      raise argparse.ArgumentTypeError("Please provide path to store output in --dir argument")

  return args

# cycletime_to_datetime
###################################


def cycletime_to_datetime(cycletime):
  '''
  Converts a cycletime string in ISO8601 format to a \
  :class:`datetime.datetime` object.
  '''
  return datetime.datetime.strptime(cycletime, "%Y%m%dT%H%MZ")

# str_to_list
###################################


def region_str_to_list(region):
  '''
  Converts a string with region coordinates
  '''
  region_list=[float(i) for i in region.split(',')]

  return region_list

# check_args
###################################

def check_args(interval,region,product):

  # Check interval is within predefined values
  if interval not in [1,3,6,24]:
      raise argparse.ArgumentTypeError("Interval available options: 1,3,6,24 "
                                       "in --int arg.")
  # Check region 
  if len(region) !=4:
      raise argparse.ArgumentTypeError("Region must be a list of E,S,W,N e.g. "
                                      "40,-20,100,50 for the Indian Ocean")
  if region[0]>region[2]:
      raise argparse.ArgumentTypeError("E coord must be lower than W in --reg ")

  if region[1]>region[3]:
      raise argparse.ArgumentTypeError("S coord must be lower than N in --reg")

  # Check Product
  if product not in ["production","NRTLate","NRTearly"]:
      raise argparse.ArgumentTypeError("Not recognized GPM-IMERG product in --prod "
                                       "It must be: 'production','NRTLate' or 'NRTearly' ")

# get_gpm_cubes
###################################

def get_gpm_cubes(time_i,region,interval,product):
  '''
  Load rainfall accumulation fields using a lambda function over the selected time
  then cut-off the region of interest and averages over time
  '''

  # Define path to extract data
  filename="{0}/{1}/{2:%Y}/gpm_imerg_{1}_{3}_{2:%Y%m%d}.nc".format(path_gpm,product,time_i,GPM_V)

  # Check if production has got time requested (may be too close to real time!)
  if product=='production' and not os.path.exists(filename):
    print(" File {:s} not found. Production has not reached this date".format(filename))
    sys.exit(1)

  #Get time constraint
  time_f=time_i + datetime.timedelta(hours=interval)
  cons_time=iris.Constraint(time=lambda cell: time_i <= cell.point <= time_f)
  # Get cubes
  gpm=iris.load_cube(filename,cons_time)
  #Extract
  gpm=gpm.intersection(longitude=[region[0],region[2]],latitude=[region[1],region[3]])
  #Average on time
  gpm=gpm.collapsed('time',iris.analysis.MEAN)

  return gpm

# gpm_cube_save
###################################

def gpm_cube_save(cube,time_i,interval,path_out):
  '''
  Saves NetCDF cube with the hourly accumulated precipitation interval chosen
  at the path_out file
  '''
  time_f=time_i + datetime.timedelta(hours=interval)

  if interval==1:
    int_dir='hourly'
  elif interval==3:
    int_dir='3hourly'
  elif interval==6:
    int_dir='6hourly'
  elif interval==24:
    int_dir='daily'
    

  #Set and make dir
  dirname=path_out+'/'+int_dir

  if not os.path.exists(dirname):
    try:
        os.makedirs(dirname)
    except OSError as exc:
      raise PermissionError('Do not have permissions to create output dir at "'+dirname+"'") from exc

  #Set output filename and save
  fileout=dirname+'/GPM_'+GPM_V+'_'+time_i.strftime('%Y%m%d%H')+'_'+time_f.strftime('%Y%m%d%H')+'.nc'
  iris.save(cube,fileout)

#                     END OF PROGRAM                                     #
##########################################################################
if __name__ == '__main__':
    main()
