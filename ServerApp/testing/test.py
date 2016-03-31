import shutil, glob

if __name__ == "__main__": 

	outfilename = '/etc/TIX/records/temp1'
	with open(outfilename, 'wb') as outfile:
	    for filename in glob.glob('/etc/TIX/records/*'):
	        with open(filename) as readfile:
	            shutil.copyfileobj(readfile, outfile)