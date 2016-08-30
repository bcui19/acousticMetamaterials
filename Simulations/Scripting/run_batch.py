import os
# import process
from subprocess import call
from time import *
from multiprocessing import Pool
from multiprocessing import Process
import numpy as np
import sys
import shutil

#define constants
SUBDIR = "pillar_simulations/test"
NUM_PORTS = 4
FILENAMES = ["v1,0,0,0", "v0,1,0,0", "v0,0,1,0", "v0,0,0,1"]#, "1v1,0,0,0", "1v0,1,0,0", "1v0,0,1,0", "1v0,0,0,1"]
FREQ_PAR = [10000,14000,5000]



#runs code aster
def start_asrun(prefix, file_comm, file_export, file_log, freq_par):
    asrun_command = "(time as_run %s) > %s 2>&1" %(file_export, file_log)

    print """
============ case run start ==============
COMM:      %s
EXPORT:    %s
LOG:       %s

FREQ SWEEP: %f : %f : %f

RUN COMMAND: %s
============================
""" %(file_comm, file_export, file_log, freq_par[0], freq_par[1], freq_par[2], asrun_command)

    call(asrun_command, shell = True)

def processingHelper(massiveRun, index, subDir, currDir):
    massiveRun.runaster(index, subDir, currDir)

def singleRunHelper(massiveRun, index):
    massiveRun.singleRun(massiveRun.subdirs[index])

def asterRunHelper(massiveRun, index, subDir, currDir):
    massiveRun.runaster(index, subDir, currDir)

class massiveRun:
    def __init__(self, freq_par):
        self.dir = os.path.dirname(__file__) 

        self.freq_par = freq_par
        self.getSubDir()
        self.initializeRun()

    def getSubDir(self):
        self.subdirs = next(os.walk(SUBDIR))[1]

    def initializeRun(self):
        resuDict = {}
        self.N_workers = 48
        pool = Pool(processes = self.N_workers)
        count = 0
        for i in range(len(self.subdirs)):
            #self.singleRun(self.subdirs[i])
            #tempResult = pool.apply_async(singleRunHelper, args = (self, i))
            subDir = self.subdirs[i]
            for j in range(NUM_PORTS):
                currDir = FILENAMES[j]
                self.createFiles(j, subDir, currDir)
                tempResult = pool.apply_async(asterRunHelper, args = (self, j, subDir, currDir))
                count += 1
                resuDict[count] = tempResult

        for resu in resuDict:
            resuDict[resu].get()
            
            #self.singleRun(self.subdirs[i])
        pool.close()

    #performs simulations for the current geometry
    def singleRun(self, subDir):
        resuDir = {}
#        pool = Pool(processes = self.N_workers)
        for i in range(NUM_PORTS):
            currDir = FILENAMES[i]
            self.createFiles(i, subDir, currDir)



         #   tempResult = pool.apply_async(processingHelper, args = (self, i, subDir, currDir))
            self.runaster(i, subDir, currDir)
         #   resuDir[i] = tempResult

        #for resu in resuDir:
        #    resuDir[resu].get()

       # pool.close()



    #runs code aster for a given run at a given iteration
    def runaster(self, iterNum, subDir, currDir):
        currComm = os.path.join(SUBDIR, subDir, currDir, subDir + currDir + ".comm")
        currExport = os.path.join(SUBDIR, subDir, currDir, subDir + currDir + ".export")
        file_log = os.path.join(SUBDIR, subDir, currDir, "logfile.txt")

        start_asrun("temp", currComm, currExport, file_log, self.freq_par)
        

    def createFiles(self, iterNum, subDir, currDir):
        self.createVelocities(iterNum)
        print "subDir is: ", subDir
        print "currDir is: ", currDir
        self.createComm(subDir, currDir, iterNum, self.freq_par[0], self.freq_par[1], self.freq_par[2])
        self.createExport(subDir, currDir, iterNum)

    def createVelocities(self, iterNum):
        tempVelocity = [1 if i == iterNum else 0 for i in range(NUM_PORTS)]
        self.velocity = """
CHARACOU=AFFE_CHAR_ACOU( MODELE=GUIDE,
                 VITE_FACE=( _F( GROUP_MA = 'PORT1',
                               VNOR = ('RI', %u, 0.0,)),
                             _F( GROUP_MA = 'PORT2',
                               VNOR = ('RI', %u, 0.0,)),
                             _F( GROUP_MA = 'PORT3',
                               VNOR = ('RI', %u, 0.0,)),
                             _F( GROUP_MA = 'PORT4',
                               VNOR = ('RI', %u, 0.0,))
                             )
                               )
""" %(tempVelocity[0], tempVelocity[1], tempVelocity[2], tempVelocity[3])
        self.tempVelocity = tempVelocity

    def createComm(self, subDir, currDir, iterNum, lowFreq = 25000, highFreq = 30000, dFreq = 12):
        s_comm = ''
        s_comm += """
# TITRE GUIDE D'ONDE A SORTIE ANECHOIQUE (ONDES PLANES) E.F. CLASSIQUES
#            CONFIGURATION MANAGEMENT OF EDF VERSION
# ======================================================================
# COPYRIGHT (C) 1991 - 2012  EDF R&D                  WWW.CODE-ASTER.ORG
# THIS PROGRAM IS FREE SOFTWARE; YOU CAN REDISTRIBUTE IT AND/OR MODIFY
# IT UNDER THE TERMS OF THE GNU GENERAL PUBLIC LICENSE AS PUBLISHED BY
# THE FREE SOFTWARE FOUNDATION; EITHER VERSION 2 OF THE LICENSE, OR
# (AT YOUR OPTION) ANY LATER VERSION.
#
# THIS PROGRAM IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT
# WITHOUT ANY WARRANTY; WITHOUT EVEN THE IMPLIED WARRANTY OF
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. SEE THE GNU
# GENERAL PUBLIC LICENSE FOR MORE DETAILS.
#
# YOU SHOULD HAVE RECEIVED A COPY OF THE GNU GENERAL PUBLIC LICENSE
# ALONG WITH THIS PROGRAM; IF NOT, WRITE TO EDF R&D CODE_ASTER,
#    1 AVENUE DU GENERAL DE GAULLE, 92141 CLAMART CEDEX, FRANCE.
# ======================================================================
#  MODELISATION 'ACOUSTIQUE' AVEC ELEMENTS HEXA20 ET FACE8
#  GUIDE D'ONDE ACOUSTIQUE EN E.F. C...
#LASSIQUES
#

import numpy as np
import math

## input parameters
lowFreq = %d
highFreq = %d
dFreq = %d
file_impedance = '/media/2TB/ZL_l0.100_r0.010.txt'
##

DEBUT( );


BUFFSIZE=10000
u = -0.014

Pr       = [None] * BUFFSIZE
ZZ = [None] * BUFFSIZE

frequencySweep = range(lowFreq, highFreq, dFreq)

f, Zreal, Zimag = np.loadtxt(file_impedance, unpack=True)

# import the mesh as MED format
MAIL=LIRE_MAILLAGE(FORMAT='MED', )

# define the air material
AIR=DEFI_MATERIAU( FLUIDE=_F( RHO = 1.3, CELE_C = ('RI',343.,0.,)))

# set the affecter of the material on the geometry
# TOUT means everything? OUI is yes.
CHAMPMAT=AFFE_MATERIAU(  MAILLAGE=MAIL,
                         AFFE=_F( TOUT = 'OUI',  MATER = AIR) )

# define the FEM model to use. Here
GUIDE=AFFE_MODELE(  MAILLAGE=MAIL,
                    VERIF='MAILLE',
                    AFFE=_F( TOUT = 'OUI',
                             MODELISATION = '3D',
                             PHENOMENE = 'ACOUSTIQUE'), )


# CAC=AFFE_CHAR_ACOU( MODELE=GUIDE,
#                     VITE_FACE=_F(GROUP_MA='ENTREE',
#                                  VNOR=('RI',-0.014,0.,),),
#                     IMPE_FACE=_F(FROUP_MA='SORTIE',
#                                  PRES=('RI',0.,0.,),) );
#                     # PRES_IMPO=_F(GROUP_MA='SORTIE',
#                     #              PRES=('RI',0.0,0.0,),) );

u = -0.014
fake_zero = 0.0
#1E-10

# define the constant acoustic boundary condition
# here VITE_FACE is vibration velocity field
%s

## Set up matrices
n = 0
for F in frequencySweep:


    # PRESACOU=AFFE_CHAR_ACOU( MODELE=GUIDE,
    #                          PRES_IMPO=_F( GROUP_MA = 'SORTIE',
    #                                        PRES = ('RI', 0., 0.,)))
    ## Perfect end condition
    # ZZ[n]=AFFE_CHAR_ACOU( MODELE=GUIDE,
    #                          IMPE_FACE=_F( GROUP_MA = 'SORTIE',
    #                                        IMPE = ('RI', 0.000001, 0.000001,)))

    ZR = Zreal[n] if np.abs(Zreal[n]) > 1E-10 else 1E-10
    ZI = Zimag[n] if np.abs(Zimag[n]) > 1E-10 else 1E-10

    ZR = 0.0000001
    ZI = 0.0000001


    # ZZ[n]=AFFE_CHAR_ACOU( MODELE=GUIDE,
    #                         IMPE_FACE=_F( GROUP_MA = 'SORTIE',
    #                         IMPE = ('RI', ZR, ZI,..
#)))

    #ZZ[n]=AFFE_CHAR_ACOU( MODELE=GUIDE,
    #                     VITE_FACE=_F( GROUP_MA = 'SORTIE',
    #                                  VNOR = ('RI', 0, 0.,)))

    print 'Impedance Table Lookup (F,ZR,ZI) = ', F, ZR, ZI

    ## Anechoic end condition
    # IMPEACOU=AFFE_CHAR_ACOU( MODELE=GUIDE,
    #                          IMPE_FACE=_F( GROUP_MA = 'SORTIE',
    #                                        IMPE = ('RI', 445.9,0.,)))

    # compute all the matrices
    ASSEMBLAGE(  MODELE=GUIDE,
                 # CHARGE=ZZ[n], # rigid conditions?
                 CHAM_MATER=CHAMPMAT, # total elementary computation
                 CHARGE=CHARACOU,
                 NUME_DDL=CO("NU"),
                 VECT_ASSE=(_F( VECTEUR = CO("VECTASS"),OPTION='CHAR_ACOU', CHARGE=CHARACOU)),
                 MATR_ASSE=(_F( MATRICE = CO("MATASK"), OPTION = 'RIGI_ACOU'),
                            _F( MATRICE = CO("MATASM"), OPTION = 'MASS_ACOU'),)
                       )

# #-----------------------CALCUL HARMONIQUE-------------------------------

    Pr[n]=DYNA_VIBRA( TYPE_CALCUL='HARM',
                      BASE_CALCUL='PHYS',
                      MATR_MASS=MATASM,
                      MATR_RIGI=MATASK,
                      #MATR_AMOR=MATASI,
                      FREQ=F,
                      EXCIT=_F( VECT_ASSE = VECTASS,
                                COEF_MULT = 1.,
                                PUIS_PULS = 1,
                                PHAS_DEG = 90.));

    ## NOTE:
    ## www.code-aster.org/doc_doc/DOCASTER_en/An_introduction_to_Code_Aster.pdf
    ##
    ## ELGA: the calculation is done at the Gauss points of the elements
    ## ELNO: the calculation is done at the nodes of each elements, considered
    ##       separately from the neighboring elements
    ##       * more than one value are calculated for each node, one value from
    ##         each element sharing that node.
    ## NOEU: the calculation is done at each node
    ##       * A mean value of the values coming from each element sharing the
    ##         node
    Pr[n]=CALC_CHAMP( reuse=Pr[n],
                 TOUT_ORDRE='OUI',
                 RESULTAT=Pr[n],
                 ACOUSTIQUE=('INTE_NOEU', 'PRAC_NOEU')
           )


    #### For visualization: won't work if in the loop...
    ## IMPR_RESU(FORMAT='MED',
    ##           RESU=_F(RESULTAT=Pr,
    ##           PARTIE='REEL',),);
    IMPR_RESU( RESU=_F(NUME_ORDRE=1,
                       RESULTAT=Pr[n],
                       # TOUT_CHAM='OUI',
                       NOM_CHAM=('INTE_NOEU', 'PRAC_NOEU'),
                       NOM_CMP=('PRES_R', 'PRES_I', 'INTX_R', 'INTX_I', 'INTY_R', 'INTY_I', 'INTZ_R', 'INTZ_I'),
                       # TOUT='OUI' # NOEUD='NO763', #MAILLE='MA57',
                       # NOEUD=('N170') # SORTIE face middle point
                       # MAILLE=('M8814')
                       # GROUP_MA=('ENTREE', 'SORTIE1', 'SORTIE2')
                       GROUP_MA=('PORT1', 'PORT2', 'PORT3', 'PORT4')
                       )
                 )
    n += 1

    DETRUIRE (CONCEPT = _F (NOM = (NU, VECTASS, MATASM, MATASK),),);


FIN()
#
""" %(lowFreq, highFreq, dFreq, self.velocity)

        file_comm = '%s%s.comm' %(subDir , FILENAMES[iterNum])

        currDir = os.path.join(self.dir, SUBDIR, subDir, FILENAMES[iterNum])

        if not os.path.exists(currDir):
            os.makedirs(currDir)

        file_comm = os.path.join(currDir, file_comm)

        # print file_comm
        of = open(file_comm , 'w')
        of.write(s_comm)

        # return file_comm

    #really brute force method to get filenames properly arranged
    def createExportFilenames(self, subDir, currDir, iterNum):
        fullPath = os.path.abspath(self.dir)

        self.cache = os.path.join(fullPath, SUBDIR, subDir, currDir, "cache")
        self.comm = os.path.join(fullPath, SUBDIR, subDir, currDir, subDir + FILENAMES[iterNum] + ".comm")
        self.med = os.path.join(fullPath, SUBDIR, subDir, subDir + ".med")
        self.resu = os.path.join(fullPath, SUBDIR, subDir, subDir + FILENAMES[iterNum] + ".resu")
        self.rmed = os.path.join(fullPath, SUBDIR, subDir, subDir + FILENAMES[iterNum] + ".rmed")
        self.mess = os.path.join(fullPath, SUBDIR, subDir, currDir, subDir + FILENAMES[iterNum] + ".mess")


    def createExport(self, subDir, currDir, iterNum):
        self.createExportFilenames(subDir, currDir, iterNum)
        f_export = ''
        f_export += """
P actions make_etude
P debug nodebug
P mode interactif
P mpi_nbcpu 1
P mpi_nbnoeu 1
P ncpus 1
P rep_trav %s
P testlist verification sequential
P version STA11.3
A args -max_base 100000
A memjeveux 2500
A tpmax 806400.0
F comm %s D  1
F mmed %s D  20
F resu %s R  8
F rmed %s R  80
F mess %s R  6

        """ % (self.cache, self.comm, self.med, self.resu, self.rmed, self.mess)

        export_name = "%s%s.export" %(subDir, FILENAMES[iterNum])



        currDir = os.path.join(self.dir, SUBDIR, subDir, FILENAMES[iterNum])

        if not os.path.exists(currDir):
            os.makedirs(currDir)

        file_comm = os.path.join(currDir, export_name)

        of = open(file_comm, "w")
        of.write(f_export)





if __name__ == "__main__":
    massiveRun(FREQ_PAR)
    print "done"
