
import matplotlib.pyplot as plt
import iris.plot as iplt
import iris
import numpy as np
import matplotlib as matplotlib
import datetime
import cf_units
from matplotlib.colors import BoundaryNorm

latlon_tag='60W0E_3070N'

time_init='2016/09/05 00Z'
time_final='2016/10/15 00Z'

lev_field=np.linspace(0,100,21)
lev_dspread=np.linspace(10,60,6)
letters=['(a)','(b)']

datapath='../data/PB/'

##########################################################################
#                     MAIN PROGRAM, ITERATE THROUGH TIME                 #
##########################################################################
def main():

  fig = plt.figure(figsize=(18,14))

  # iterate  experiments
  for e,exp in enumerate(['hres','spread']):
    if exp=='hres':
      off=6
    elif exp=='spread':
      off=3
    plt.subplot(2,1,e+1)
    print '++++ Doing '+exp
    # Get cube of Z500 error rate
    cube=create_plotting_array(exp,False)

    #Plot diagonal lines
    plot_diagonal_lines(cube,exp)

    #Plot Z500 error rate
    dt_init=[ datetime.timedelta(hours=time-off) + datetime.datetime.strptime('19700101','%Y%m%d') for time in cube.coord('forecast_reference_time').points]
    dt_init.append(datetime.timedelta(hours=cube.coord('forecast_reference_time')[-1].points[0]+off) + datetime.datetime.strptime('19700101','%Y%m%d'))
    print dt_init
    Tp_list=cube.coord('forecast_period').points-3
    Tp_list=np.append(Tp_list,cube.coord('forecast_period')[-1].points[0]+3)

    #Plot colormesh
    cmap = plt.get_cmap('gnuplot2_r')
    norm = BoundaryNorm(lev_field, ncolors=cmap.N, clip=True)
    ax=plt.pcolormesh(dt_init, Tp_list, cube.data, cmap=cmap, norm=norm)

    add_barriers_label()

    #Set up nice labels and axis for subplot
    set_axis_labels(exp,e)

  #Place colorbar and save plot
  save_p_cbar(ax)

##########################################################################
#                          AUX PROGRAMS                                  #
##########################################################################

def create_plotting_array(exp,prod):

  #Put init and final into datetime structures
  init_dt=datetime.datetime.strptime(time_init,'%Y/%m/%d %HZ')
  final_dt=datetime.datetime.strptime(time_final,'%Y/%m/%d %HZ')

  if prod:

    #Define datafile
    datafile=datapath+exp+'_timeseries_2016090500_2016101800_60W0E_3070N.nc'

    ### Build cube_all
    cube_all=iris.cube.CubeList()

    ### Create new coordinates
    time_iter=init_dt
    while time_iter <=final_dt:

      for Tp in range(3,168+3,6):
        print time_iter,Tp
        cons_Tp=iris.Constraint(forecast_period=lambda cell: Tp-3 <=cell <=Tp+3)
        cons_period=iris.Constraint(forecast_reference_time=time_iter)
        newcube=iris.load_cube(datafile,cons_Tp & cons_period)

        mean_cube=newcube.collapsed('forecast_period',iris.analysis.MEAN)

        dErr_point=(newcube[1]-newcube[0])/6

        dErr_point.add_aux_coord(mean_cube.coord('forecast_period'))

        cube_all.append(dErr_point)
      if exp=='em' or exp=='spread':
        time_iter = time_iter + datetime.timedelta(hours=6)
      else:
        time_iter = time_iter + datetime.timedelta(hours=12)

    # Merge cube
    cube_all=cube_all.merge_cube()

    #Compute m/days
    cube_all.data=cube_all.data*24.

    iris.save(cube_all,'../data/PB/'+exp+'_dERR_'+init_dt.strftime('%Y%m%d%H')+'_'+final_dt.strftime('%Y%m%d%H')+'_60W0E_3070N.nc')

  else:
    cons_fcst=iris.Constraint(forecast_reference_time=lambda cell: init_dt <=cell.point <= final_dt)
    cube_all=iris.load_cube(datapath+exp+'_dERR_'+init_dt.strftime('%Y%m%d%H')+'_'+final_dt.strftime('%Y%m%d%H')+'_60W0E_3070N.nc',cons_fcst)

  return cube_all

# plot_diagonal_lines
#############################################

def plot_diagonal_lines(cube,exp):


  date_iter=datetime.datetime.strptime(time_init,'%Y/%m/%d %HZ')
  date_end=datetime.datetime.strptime(time_final,'%Y/%m/%d %HZ')

  #Exetend 7 days to plot smaller lines left-bottom and right-upper corners
  date_iter = date_iter - datetime.timedelta(days=7)
  date_end = date_end + datetime.timedelta(days=7)

  # Loop over days
  while date_iter <= date_end:

    fcst_init_list=[]
    fcst_Tp_list=[]

    #Do loop over T+ ...
    for Tp in cube.coord('forecast_period').points:

      valid_time=date_iter - datetime.timedelta(hours=Tp)

      if valid_time >= datetime.datetime.strptime(time_init,'%Y/%m/%d %HZ') and valid_time <= datetime.datetime.strptime(time_final,'%Y/%m/%d %HZ'):
        fcst_init_list.append(valid_time)
        fcst_Tp_list.append(Tp)

    plt.plot(fcst_init_list,fcst_Tp_list,'g',linewidth=1.)
    #Iterate one more day
    date_iter = date_iter + datetime.timedelta(hours=24)


# add_barriers_label()
#############################################
def add_barriers_label():

  barriers={
  'A':[datetime.datetime.strptime('2016/09/16 00Z','%Y/%m/%d %HZ')],
  'B':[datetime.datetime.strptime('2016/09/23 00Z','%Y/%m/%d %HZ')],
  'C':[datetime.datetime.strptime('2016/09/28 00Z','%Y/%m/%d %HZ')],
  'D':[datetime.datetime.strptime('2016/10/01 00Z','%Y/%m/%d %HZ')],
  'E':[datetime.datetime.strptime('2016/10/04 00Z','%Y/%m/%d %HZ')],
  'F':[datetime.datetime.strptime('2016/10/09 12Z','%Y/%m/%d %HZ')],
  'G':[datetime.datetime.strptime('2016/10/11 12Z','%Y/%m/%d %HZ')]
  }

  for barrier in barriers:
    plt.text(barriers[barrier][0]-datetime.timedelta(hours=12),12,barrier,fontsize=36,color='g')
    plt.text(barriers[barrier][0]-datetime.timedelta(hours=150),150,barrier,fontsize=36,color='g')

# set_axis_labels
#############################################

def set_axis_labels(exp,e):

  plt.ylabel(r'$f$ (hours)',fontsize=20)
  if exp=='hres':
    plt.title(r"(a) $\partial_{f}\  E$",fontsize=24)
  elif exp=='spread':
    plt.title(r"(b) $\partial_{f}\ \sigma$",fontsize=24)
    plt.xlabel(r'$s$ ( Sept/Oct 2016)',fontsize=20)


  ## X axis
  plt.gca().xaxis.set_major_locator(matplotlib.dates.DayLocator())
  plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d'))

  #Set limits
  plt.yticks(np.arange(12,168+12,12))
  plt.gca().grid(b=True,which='major')
  plt.gca().set_ylim([3,168])



# save_p_cbar
#############################################

def save_p_cbar(ax):

   # Place colorbar
   colorbar_axes = plt.gcf().add_axes([0.2, 0.04, 0.6, 0.01])
   colorbar = plt.colorbar(ax, colorbar_axes, orientation='horizontal')
   colorbar.set_label("[m/day]",fontsize=12)

   #Save plot
   plt.savefig('../Figures/Figure_01_COLORMESH.png')
   plt.close()


#                     END OF PROGRAM                                     #
##########################################################################
if __name__ == '__main__':
    main()
