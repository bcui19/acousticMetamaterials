
import os
import sys
import re
import numpy as np
import csv

DIR = "Simulation Results/Mesh_0.002_Results"

FREQ  = 10000.   # 10kHz
OMEGA = 2. * np.pi * FREQ
CELLSIZE = 0.006 # 6mm

RHO = 1.3        # air density: 1.3 kg/m^3
SOUNDSPEED = 343.# m/s
WAVELENGTH = SOUNDSPEED / FREQ

def updateClass(dir = DIR):
    global DIR
    DIR = dir


class effectiveParamsEval:
    PTN = re.compile(r""".*unit_cell_H(\d+\.\d*)_L(\d+\.\d*)_R(\d+\.\d*).npy""")

    def __init__(self, filename, exportFile):
        try:
            print "filename is: ", filename
            (H,L) = self.extractParams(filename)
            print 'H = %f, L = %f' % (H,L)
            self.H = H
            self.L = L
            cDir = os.path.dirname(__file__)
            filepath = os.path.join(cDir, DIR, filename)

            self.Tmatrix = np.load(filepath)
            
            print self.Tmatrix
            print "The dot product between the two matricies is: ", np.dot(self.Tmatrix, self.Tmatrix)
            Lomega = CELLSIZE * OMEGA
            self.rho = self.Tmatrix[0,1].imag/ Lomega
            self.lamb = -Lomega / self.Tmatrix[1,0].imag
            print "--------------------------------------------"
            print "Wave Len %f" % WAVELENGTH
            print "--------------------------------------------"
            print self.rho, RHO
            print self.lamb, RHO * SOUNDSPEED*SOUNDSPEED

            self.exportFile = exportFile

        except TypeError:
            print("it has to be a csv file")             

    def exportFile(self):
        self.exportCSV()

    def returnRho(self):
        return self.rho
    
    def returnLambda(self):
        return self.lamb

    def returnL(self):
        return self.L
    
    def returnH(self):
        return self.H

    def extractParams(self, filename):
        ret = effectiveParamsEval.PTN.match(filename)
        if ret is None: 
            return
            #raise Exception('cannot parse the filename: %s' % filename)
        return ( float(ret.group(1)), float(ret.group(2)) )


def main():
    Cdir = os.path.dirname(__file__)
    currDir = os.path.join(Cdir, DIR)
    dirListing = os.listdir(currDir)
    for dir in dirListing:
        effectiveParamsEval(dir)


#if __name__ == "__main__":
#    main()




