# 21 January 2022 
# Maegan Jennings, Ozzy Weinreb 

import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import scipy as sc
import datetime
from scipy import stats
from .DataHolder import DataHolder
from .simple import ceil



class AveragedRats:
    # THIS IS A DISASTER ZONE, DO NOT ATTEMPT TO USE THIS CLASS YET 

    # all of the colors for the plotting. We'll have issues if there are more than 8 rat groups compared simultaneously. 
    farben= ['xkcd:dark red','xkcd:burnt orange', 'xkcd:goldenrod', 'xkcd:forest green', 'xkcd:royal blue','xkcd:dark purple', 'xkcd:violet', 'xkcd:rose']

    def __init__(self, ratdata, ratname):
        """ Class for plotting the rat data. This works on a single rat group's data, or a few rat groups' data. 
        Interacts with the DataAvgs objects. 
        
        Parameters 
        ---- 
        ratdata : object or list
            Name(s) of the object returned from the DataAvgs class
        ratname : string or list
            Name(s) of the rat to be displayed on the plots. 
        """
                   
        self.rattitle = ratname
        self.rat = ratdata



    def Plot(self, ptype = 'IPI', target = 700, window = 1000, minwindow = 100, error = 10, boxcar = 300):
        """ Returns a plot of the average 1st tap length and average IPI for each session. 
        
        Parameters 
        ---- 
        ptype : str
            REQUIRED
            Name of the plot that you want to make. 
            allowed strings: "IPI", "Success", "Tap1", "Tap2" 

        target : int 
            REQUIRED
            Number value of the target IPI desired 
            Default is 700 
        
        window : int 
            REQUIRED
            Number for the window for moving average calculatons 
            Default is 1000 

        minwindow : int 
            REQUIRED
            Number for the minimum window for moving average calculatons 
            Default is 100
        
        error : int
            Only required for Success plots
            Number for the error margins for the Success plots. 
            Default is 10% 

        boxcar : int
            Only required for the coefficient of variation plots
            Number for the window length for the moving average "smoothing" function
            Default is 300
        
        Returns 
        ---- 
        unnamed : matplotlib plot 
        """
        
        
        # Graph of Tap1 & IPI vs. trials 
        if ptype == ("Tap1" or "tap1"):
            self.Tap_vIPI(1, target, window, minwindow)

        # Graph of Tap2 & IPI vs. trials 
        elif ptype == ("Tap2" or "tap2"):
            self.Tap_vIPI(2, target, window, minwindow) 

        # Graph of IPI vs. trials 
        elif ptype == "IPI":
            self.IPI(target, window, minwindow)

        # Graph of Success vs. trials 
        elif ptype == "Success":
            self.Success(target, error, window, minwindow)

        elif ptype == "CV":
            self.CV(target, window, minwindow, boxcar)


    def Tap_vIPI(self, tap, target, window, minwindow):
        """ Here """
        # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 

        # define the plotting style 
        plt.style.use('default')
        
        # now that all posibilities of self.rat are lists
        for rat, name in zip(self.rat, self.rattitle):
            # Find the index of the correct dataframe within the targetframe object
            i = rat.Find_i(target)
            # grab the correct dataframe
            data = rat[i] 
            # define the interval
            interval = data.MovingAverage('interval', win = window, minwin = minwindow)
            # find the moving average of the tap length
            if tap == 1:
                taps = data.MovingAverage('tap_1_len', win = window, minwin = minwindow)
            else:
                taps = data.MovingAverage('tap_2_len', win = window, minwin = minwindow) 
            
            # make a list for the trials 
            trials = range(len(interval))

            # plot 
            plt.scatter(trials, taps, label= f'{name}, Tap {tap}')
            plt.scatter(trials, interval, label=f'{name}, IPI')
        
        # plot a line at where the target should be. 
        plt.hlines(target, 0, len(interval), 'xkcd:light grey', label="target")

        # add things to the plot that only need to be added once. 
        plt.xlabel('Trial Number')
        plt.ylabel('Time (ms)')
        plt.title(f'Tap {tap} & Interval')
        plt.legend()
        plt.show()


    def IPI(self, target, window, minwindow):
        """ Returns a plot of the coefficient of variation for all of the rats that you give it 

        Params 
        --- 
        ratlist : list of dataframes
        List of the averaged dataframes that come from DataAvgs

        target : int
        Number of the target you're looking at

        window : int
        The number of sessions that should be used to calculate the moving coefficient of variation. 
        Default is a window of 100

        boxcar : int 
        The number of sessions that is used to smooth the Coefficient of variation data. 
        Default is a window of 300
        """

        # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 

        # So plots show up on a dark background VSCode
        plt.style.use('default')

        # for each of the rats being plotted, 
        for r in range(len(self.ratlist)): 
            # find the coefficient of variation for this rat and then plot it. 
            success = self.ratlist[r].Avgd_Interval(target, avgwindow = window, minwin = minwindow)
            
            # define the x axis based on the length of the successes
            trials = range(success.shape[0])
            # plot with a different color for each rat in the ratlist. 
            plt.plot(trials, success, color = self.farben[r], label=f'{self.names[r]} group')
            # just making the plot look nice
        plt.xlabel('Trial Number')
        plt.ylabel(f' Interval (miliseconds')
        plt.title(f'IPI for {target}ms target IPI')
        plt.legend()
        plt.show() 


    def Success(self, target, error, window, minwindow): 
        """ Returns a plot of the coefficient of variation for all of the rats that you give it 
        
        Params 
        --- 
        ratlist : list of dataframes
            List of the averaged dataframes that come from DataAvgs
        
        target : int
            Number of the target you're looking at
        
        window : int
            The number of sessions that should be used to calculate the moving coefficient of variation. 
            Default is a window of 100
        
        boxcar : int 
            The number of sessions that is used to smooth the Coefficient of variation data. 
            Default is a window of 300
        
        Returns 
        --- 
        plot
        """

        # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 
       
        # So plots show up on a dark background VSCode
        plt.style.use('default')

        # for each of the rats being plotted, 
        for r in range(len(self.ratlist)): 
            # find the coefficient of variation for this rat and then plot it. 
            success = self.ratlist[r].TrialSuccess(target, error, avgwindow = window)
            # crop the first 10 trials because some start at 100% and then plummet which makes the graph look wonky.
            #success = success[10:]
            # define the x axis based on the length of the successes
            trials = range(success.shape[0])
            # plot with a different color for each rat in the ratlist. 
            plt.plot(trials, success, color = self.farben[r], label=f'{self.names[r]} group')
        # just making the plot look nice
        plt.xlabel('Trial Number')
        plt.ylabel(f'Percent of trials within limit (moving {window} trial window) ')
        plt.title(f'Success Rate within +-{error}% of {target}ms target IPI')
        plt.legend()
        plt.show() 


    def CV(self, target, window, minwindow, boxcar): 
        """ Returns a plot of the coefficient of variation for all of the rats that you give it 
        
        Params 
        --- 
        ratlist : list of dataframes
            List of the averaged dataframes that come from DataAvgs
        
        target : int
            Number of the target you're looking at
        
        window : int
            The number of sessions that should be used to calculate the moving coefficient of variation. 
            Default is a window of 100
        
        boxcar : int 
            The number of sessions that is used to smooth the Coefficient of variation data. 
            Default is a window of 300
        
        Returns 
        --- 
        plot
        """
       # check to see if the rats are in a list. If not, that means there is only one rat in the list. 
        if not isinstance(self.rat, list): 
            # make the item into a "list" so it can be iterated over the same code. 
            self.rat = [self.rat] 
        
        plt.style.use('default')
        for r in range(len(self.ratlist)): 
            # find the coefficient of variation for this rat and then plot it. 
            cv, i = self.ratlist[r].Variation(target, avgwindow = window, boxcar = boxcar)
            trials = range(cv.shape[0])
            # plot with a different color for each rat in the ratlist. 
            plt.plot(trials, cv, color = self.farben[r], label=f'{self.names[r]} group')
        plt.xlabel('Trial Number')
        plt.ylabel('Coefficient of Variation')
        plt.title(f'Coefficient of Variation for {target}ms target IPI')
        plt.ylim([0,0.4])
        plt.legend()
        plt.show()