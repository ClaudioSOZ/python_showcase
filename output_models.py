import os
import datetime

cyclone='HAGIBIS'

##########################################################################
#                           MAIN PROGRAM                                 #
##########################################################################
def main():

  # extract obs for given cyclone
  os.system("grep "+cyclone.upper()+" global_coupled_NWP.html > cyclone_model.txt")

  times,Tp,lon,lat,pmsl,spd=set_arrays()

  #Initialize Tp_last
  Tp_last='-6'
  No_storm=True

  #Get time
  f=open('cyclone_model.txt','r')
  for i in f.readlines():
    data=i[4:].split()
    #Save storm at the from previous forecast if is new or lower than previous one
    # and reset arrays
    # If there is a forecast save it!
    if data[-1] !='****':
        save=get_cond_save(Tp_last,data[6],No_storm)
        if save:
            print '++++ '+data[6],Tp_last
            print_storm(fcst_init,times,Tp,lon,lat,pmsl,spd)
            times,lon,lat,Tp,pmsl,spd=set_arrays()

        time_TC=datetime.datetime.strptime(data[2]+data[3]+data[4]+data[5],'%Y%m%d%H')
        Tp_init=int(data[6])
        fcst_init=time_TC - datetime.timedelta(hours=Tp_init)
        print '--',fcst_init,data[6],save,No_storm
        #Copy variables to array
        times.append(datetime.datetime.strptime(data[2]+data[3]+data[4]+data[5],'%Y%m%d%H'))
        Tp.append(data[6])
        lat.append(data[10])
        lon.append(data[11])
        pmsl.append(data[20])
        spd.append(data[21])

        #Set Logical to true
        No_storm=False

    # Keep record of last forecasts
    Tp_last=data[6]


  f.close()
  os.system("rm -f cyclone_model.txt")

##########################################################################
#                           AUXILIARY PROGRAM                            #
##########################################################################

def set_arrays():

    times=[]
    Tp=[]
    lon=[]
    lat=[]
    pmsl=[]
    spd=[]

    return times,Tp,lon,lat,pmsl,spd

################################################

def print_storm(fcst_init,times,Tp,lon,lat,pmsl,spd):

  #### Print storms
  outfile = open('glm_cpl_'+fcst_init.strftime('%Y%m%d%H')+'_'+cyclone.upper(),"w+")
  for t,time in enumerate(times):
    if time.year >= 2016:
# Example of format:
#    1200UTC 09.08.2019   12  27.3N 122.0E      945            70
      tshow=time.strftime('%H%MUTC %d.%m.%Y')
      fcst='{: >3}'.format(Tp[t])
      lat_lon='{: >5}'.format(lat[t])+' '+'{0: >6}'.format(lon[t])
      p_show='{: >4}'.format(pmsl[t])
      s_show='{: >3}'.format(spd[t])
      outfile.write(' '*4+tshow+' '*2+fcst+' '*2+lat_lon+' '*5+p_show+' '*11+s_show+'\n')

  outfile.close()
################################################
def get_cond_save(Tp_last,Tp,No_storm):

    if Tp_last[-4:] == '****':
        save=True
    elif int(Tp_last) >= int(Tp):
        save=True
    else:
        save=False

    if No_storm:
        save=False

    return save

  #                     END OF PROGRAM                                     #
##########################################################################
if __name__ == '__main__':
    main()
