import get_transmission_matrix as gtm

def main():
	tm = gtm.transmissionMatrix("fileCheck_cube/solidWorks.txt",1)
	tm2 = gtm.transmissionMatrix("fileCheck_cube/salome.txt",1)
	rtm = tm.returnTransmissionMatrix()
	rtm2 = tm.returnTransmissionMatrix()
	gtm.checkMatrix.main(rtm, rtm2)

main()
