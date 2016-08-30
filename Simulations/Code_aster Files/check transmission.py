import get_transmission_matrix as gtm
import check_transmission_matrix as ctm


def main():
	fileDirectory = "Old Files/Checks"
	paths = [fileDirectory + "/v2_" + str(i) for i in [1, 3, 5]]
	tempOutput = "temp"

	tm1 = gtm.transmissionMatrix(paths[0] + "/filenames.txt", paths[0], "filenames listenNode.txt", tempOutput, 1)
	tm3 = gtm.transmissionMatrix(paths[1] + "/filenames.txt", paths[1], "filenames listenNode.txt", tempOutput, 3)
	tm5 = gtm.transmissionMatrix(paths[2] + "/filenames.txt", paths[2], "filenames listenNode.txt", tempOutput, 5)

	rtm1 = tm1.returnTransmissionMatrix()
	rtm3 = tm3.returnTransmissionMatrix()
	rtm5 = tm5.returnTransmissionMatrix()

	# print rtm1

	ctm.main(rtm1, rtm3)
	ctm.main(rtm1, rtm5)

	# fileDirectory = "Paper/Paper Copy Actual Size"
	
	# tm = gtm.transmissionMatrix(fileDirectory + "/paperCheck.txt", fileDirectory, "collimator listennode.txt", tempOutput, 1)

main()