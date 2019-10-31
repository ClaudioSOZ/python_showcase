import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cartopy

import cartopy.feature as cfeature
import datetime

storm='YUTU'
days_to_pick=['21/10/2018', '2/11/2018']
dates=['20181021','20181022','20181023','20181024','20181025','20181026','20181027','20181028','20181029','20181030','20181031','20181101','20181102']

jobs={
'OBS':['OBS','k',2,'-','x'],
'u-bn245':['uncpl','g',1,'-','x'],
'u-bn252':['cpl','b',1,'-','x'],
}

coastline = cfeature.NaturalEarthFeature(   category='Physical',
                                              name='coastline',
                                              scale='50m',
                                              facecolor='none')

days_marker={'1':['x'],'2':['<'],'3':['d'],'4':['8'],'5':['p'],'6':['+'],'7':['.'],'6':['x'],'8':['<'],'9':['d'],'10':['>'],'11':['*'],'12':['^'],'13':['s'],
'14':['8'],'15':['p'],'16':['+'],'17':['.'],'18':['x'],'19':['<'],'20':['d'],'21':['>'],'22':['*'],'23':['^'],'24':['s'],'25':['x'],'26':['<'],'27':['d'],'28':['>'],
'29':['*'],'30':['^'],'31':['s']
}


##########################################################################
#                           MAIN PROGRAM                                 #
##########################################################################
def main():

  for date in dates:
    do_TC_plot(date)

##########################################################################
#                           AUX. PROGRAMS                                #
##########################################################################

def do_TC_plot(date):

  # Set up plot
  fig = plt.figure(figsize=(14,6))
  #plt.suptitle(storm+' '+date,fontsize=20)
  # Plot trajectory
  plt.subplot(1,2,1, projection=cartopy.crs.PlateCarree())
  plot_traj(date)

  # Plot PMSL
  ax = plt.subplot(2,2,2)
  plot_pmsl(ax,date)

  #Plot WIND SPEED
  ax = plt.subplot(2,2,4)
  plot_winds(ax,date)

  #Save plot
  plot_name=storm+'_'+date
  plt.savefig('../plots/'+plot_name+'.png')
  print 'Saved '+plot_name+'.png'
  plt.close()


# plot_traj
#
# This script calls read_in_tracks and plots the
# trajectory of the cyclone
###########################################################

def plot_traj(date):

 #Iterate through jobs
 for j,job in enumerate(jobs):
   print '-------- plot_traj '+job+' '+date
   time,lat,lon,pmsl,spd=read_in_tracks(date,job)

   #Plot track
   plt.plot(lon,lat,c=jobs[job][1],marker=jobs[job][4],lw=jobs[job][2],ls=jobs[job][3],markersize=4)

   #Plot days with an X, initialize the loop
   m=0
   for h,time_hr in enumerate(time):
       if time_hr.hour == 0:
         daym=str(time_hr.day)
         if job =='OBS':
           plt.plot(lon[h],lat[h],c=jobs[job][1],marker=days_marker[daym][0],markersize=8,mew=2,markeredgecolor=jobs[job][1],label=daym)
         else:
           plt.plot(lon[h],lat[h],c=jobs[job][1],marker=days_marker[daym][0],markersize=8,mew=2,markeredgecolor=jobs[job][1])
         m=m+1

   #Get box for plotting
   if job =='OBS':
     box=get_box(lat,lon)

 #Set axis and add coastlines
 gl=plt.gca().gridlines(draw_labels=True)
 gl.xlabels_top = False
 gl.ylabels_right = False

 plt.legend(numpoints=1,fontsize=8,loc='best')
 plt.gca().add_feature(coastline)

 plt.xlim([box[0],box[2]])
 plt.ylim([box[1],box[3]])
 plt.ylabel('Latitude',fontsize=14)
 plt.xlabel('Longitude',fontsize=14)

# plot_pmsl
#
# This script calls read_in tracks and plots the PMSL
# intensity of the cyclone
###########################################################

def plot_pmsl(ax,date):

  #Iterate through jobs
  for j,job in enumerate(sorted(jobs)):
    time,lat,lon,pmsl,spd=read_in_tracks(date,job)

    # Set tag. include day for fcst
    if job == 'OBS':
      label_tag=jobs[job][0]
    else:
      label_tag=jobs[job][0]+' '+datetime.datetime.strptime(date,'%Y%m%d').strftime('%d/%m')

    # Do plot
    plt.plot(time,pmsl,c=jobs[job][1],marker=jobs[job][4],lw=jobs[job][2],ls=jobs[job][3],label=label_tag)

  plt.legend(numpoints=1,fontsize=12,loc='best')
  plt.ylabel('PMSL (mb)',fontsize=12)
  #plt.ylim([900,1020])
  #Get days in the x axis
  #plt.xaxis('tight')
  plt.gca().xaxis.set_major_locator(mdates.DayLocator())
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))
  plt.gca().grid(b=True,which='major')

# plot_winds
#
# This script calls read_in tracks and plots the wind speed
# cyclone
###########################################################

def plot_winds(ax,date):

  #Iterate through jobs
  for j,job in enumerate(sorted(jobs)):
    time,lat,lon,pmsl,spd=read_in_tracks(date,job)
    #Plot Int
    label_tag=jobs[job][0]+' '+datetime.datetime.strptime(date,'%Y%m%d').strftime('%d')
    #Only plot Sarika ones
    plt.plot(time,spd,c=jobs[job][1],marker=jobs[job][4],lw=jobs[job][2],ls=jobs[job][3])

  plt.ylabel('MAX WIND SPEED (knots)',fontsize=12)
  #plt.ylim([900,1020])
  #Get days in the x axis
  #plt.xaxis('tight')
  plt.gca().xaxis.set_major_locator(mdates.DayLocator())
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))
  plt.gca().grid(b=True,which='major')

# get_box
#
# Get The lat-lon box to plot
###########################################################

def get_box(lat,lon):

  off_lat=5
  off_lon=5

  box=[int(min(lon)-off_lon),int(min(lat)-off_lat),int(max(lon)+off_lon),int(max(lat)+off_lat)]

  return box


# read in tracks
#
# Reads in track files and output time,lat,lon and PMSL
# for the exp
###########################################################

def read_in_tracks(date,job_tag):
  #Define arrays
  time_all=[]
  lat_all=[]
  lon_all=[]
  pmsl_all=[]
  spd_all=[]
  #Read in data
  if job_tag=='OBS':
    f=open('../MOTC_output/'+job_tag+'_'+storm,'r')
  else:
    f=open('../MOTC_output/'+job_tag+'_'+date+'_'+storm,'r')

  f.readline()
  f.readline()
  f.readline()


  for i in f.readlines():
    if i.split():
      #Get time
      time_str=' '.join(i.split()[0:2])
      time_dt=datetime.datetime.strptime(time_str,'%H%MUTC %d.%m.%Y')
      time_match=time_dt>=datetime.datetime.strptime(days_to_pick[0],'%d/%m/%Y') and time_dt<=datetime.datetime.strptime(days_to_pick[1],'%d/%m/%Y')
      if time_match:
#        print( date, job_tag,time_dt)
        lat_all.append(float(i.split()[3][:-1]))
        lon_all.append(float(i.split()[4][:-1]))
        pmsl_all.append(float(i.split()[5]))
        spd_all.append(float(i.split()[6]))
        time_all.append(time_dt)

  f.close()

  return time_all,lat_all,lon_all,pmsl_all,spd_all

#                     END OF PROGRAM                                     #
##########################################################################
if __name__ == '__main__':
    main()
