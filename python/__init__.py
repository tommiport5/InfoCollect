LOCAL_ADDR = ('localhost', 48484)
Socket2 = ('localhost', 48485)
App = 'InfoCollect'
ComPath = "/var/lib/misc/"
File = {'G':"gas", 'D':"gas", 'F':"gas.final", 'X':"temp", 'T': 'temp', 'H':"hum", 'L':"light", 'A': "all", 'P': 'press'}

from multiprocessing import Lock

mutex = {'H':Lock(), 'A':Lock(), 'T':Lock(), 'L':Lock(), 
         'G':Lock(), 'D':Lock(), 'P':Lock(), 'F': Lock(),
         'X':Lock(), 'b': Lock()}
		 
