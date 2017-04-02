import socket                   
import subprocess
import os
import re
import hashlib
import sys
from datetime import datetime
conn = socket.socket()     
import time
host = ""
sport = 12276         
conn.bind((host, sport))
conn.listen(5)
#print 'Server listening....'
def file_type(filename):
	p = subprocess.Popen('file '+filename, shell=True, stdout=subprocess.PIPE).stdout.read()
	output = p.split(' ')[1]
	return output
def longlist():
	allfiles = os.listdir('.')
	onlyfiles = []
	output = ""
	for file in allfiles:
		ftype = ""
		if not os.path.isdir(file):
			ftype = "file-"
		filename, file_extension = os.path.splitext(file)
		file_name = filename
		file_size = os.stat(file).st_size
		file_modified_time = time.ctime(os.path.getmtime(file))
		output+="name: " + file +" "+" size: " + str(file_size) + " " + " last_modified: " + str(file_modified_time) + " type: "  +ftype+str(file_type(file))+ "\n"
	return output
def voidstring():
	e = " "
	for p in range(0,1025):
		e += " "
	return e
def shortlist(stime,etime):
	allfiles = os.listdir('.')
	start = datetime.strptime(stime, '%d/%m/%Y')
	end = datetime.strptime(etime, '%d/%m/%Y')
	onlyfiles = []
	output = ""
	for file in allfiles:
		ftype = ""
		last_modified_time = datetime.fromtimestamp(os.path.getmtime(file))
		if not os.path.isdir(file):
			ftype = "file-"
		if last_modified_time >= start and last_modified_time <= end:
			filename, file_extension = os.path.splitext(file)
			file_name = filename
			file_size = os.stat(file).st_size
			file_modified_time = time.ctime(os.path.getmtime(file))
			output+="name: " + file +" "+" size: " + str(file_size) + " " + " last_modified: " + str(file_modified_time) + " type: "  + ftype+str(file_type(file))+ ")\n"
	return output

def regex(pattern):
    allfiles = os.listdir('.')
    onlyfiles = []
    output = ""
    for file in allfiles:
    	ftype = ""
    	if not os.path.isdir(file):
    		ftype = "file-"
		if not os.path.isdir(file):
			filename, file_extension = os.path.splitext(file)
			regexPattern = re.compile(str(pattern))
			file_name = filename
			file_size = os.stat(file).st_size
			file_modified_time = time.ctime(os.path.getmtime(file))
			if re.search(regexPattern,file):
				output+="name: " + file +" "+" size: " + str(file_size) + " " + " last_modified: " + str(file_modified_time) + " type: "  + ftype+str(file_type(file))+ '\n'
    return output
def listWithDir():
	allfiles = os.listdir('.')
	output = []
	for file in allfiles:
		output += file
		if not os.path.isdir(file):
			output += " file "
		else:
			output += " directory "
	return output
def verify(filename):
	try:
		file_modified_time = time.ctime(os.path.getmtime(filename))
		command = "checksum: "+ str(md5(filename)) + " last_modified: " + str(file_modified_time)
		return command + "\n"
	except:
		print "invalid"
def md5(filename):
	try:
	    hash_md5 = hashlib.md5()
	    with open(filename, "rb") as f:
	        for chunk in iter(lambda: f.read(4096), b""):
	            hash_md5.update(chunk)
	    return hash_md5.hexdigest()
	except Exception as e:
		print(e)
def filepermission(filename):
	return oct(os.stat(filename).st_mode)
def checkall():
	allfiles = os.listdir('.')
	onlyfiles = []
	output = ""
	for file in allfiles:
		if not os.path.isdir(file):
			output += "file: " + file + " " + verify(file)
	return output
def upload(port,filename):
	try:
		if port == "TCP":
			fp = open(filename, 'rb')
			lp = fp.read(1024)
			while lp :
				s.send(lp)
				lp = fp.read(1024)
			fp.close()
		elif port == "UDP":
			Sudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			Pudp = int(sport)+11
			Hudp = socket.gethostname()
			fp = open(filename, 'rb')
			data = fp.read(10240)
			while data :
				if Sudp.sendto(data,(Hudp,Pudp)):
					print "sending"
					data = fp.read(10240)
			Sudp.close()
			fp.close()
	except:
		print "permission denied"
def uploadinfo(filename):
	file_size = os.stat(filename).st_size
	file_modified_time = time.ctime(os.path.getmtime(filename))
	return "file: " + filename + " " +"filesize: " + str(file_size) + " last_modified: " + str(file_modified_time) + " hash: "+ str(md5(filename))
while True:
    s, addr = conn.accept()
    #print 'Got connection from', addr
    data = s.recv(1024)
    allarg = sys.argv
    if not os.path.exists(allarg[1]):
    	os.makedirs(allarg[1])
    os.chdir(allarg[1])
    #print('Server received', repr(data))
    while True:
    	    command = ""
	    #print('receiving data...')
	    data = s.recv(1024)
	    #print('data=%s', (data))
	    arr = data.split(' ')
	    if arr[0] == "index" :
	    	if len(arr) == 1:
	    		command = "index <flag> <arg> required"
	    		s.send(command)
	    		continue
	    	if arr[1] == "longlist":
	    		
			command = longlist()
			#print command
	    	elif arr[1] == "shortlist":
	    		if len(arr) == 4:
	    			stime = arr[2]
	    			etime = arr[3]
	    			command = shortlist(stime, etime)
	    		else:
	    			command = "index shortlist <stime> <etime> required"
	        elif arr[1] == "regex":
			command = regex(arr[2])+ " "
	        f = s.send(command)
	    elif arr[0] == "hash":
		if arr[1] == "verify" :
			filename = arr[2]
			file_modified_time = time.ctime(os.path.getmtime(filename))
			command = "checksum: "+ str(md5(filename)) + " last_modified: " + str(file_modified_time)
	        elif arr[1] == "checkall" :
			command = checkall()
	        f = s.send(command)
	    elif arr[0] == "download":
	    	upload(arr[1],arr[2])
	        
	    elif arr[0] == "downloadedinfo":
	    	command = uploadinfo(arr[1])
	        f = s.send(command)
	    elif arr[0] == "md5hash":
	    	command = str(md5(arr[1]))
	        f = s.send(command)
	    elif arr[0] == "filenames":
	    	files = os.listdir('.')
	    	i = ""
	    	for t in files:
	    		ftype = "dir"
	    		if not os.path.isdir(t):
	    			ftype = "file"
	    		i += t+ " "
	    		i += str(os.path.getmtime(t))+ " "
	    		i += ftype + " "

	    	command = i
	        f = s.send(command)
	    elif arr[0] == "filepermission":
	    	s.send(filepermission(arr[1]))
	    elif arr[0] == "chdir":
	    	os.chdir(arr[1])
	    	s.send("done")
	    elif arr[0] == "copy":
	    	try:
	    		upload("TCP",arr[1])
	    	except:
	    		print "not found"
			#command = subprocess.Popen("ls -l", shell=True, stdout=subprocess.PIPE).stdout.read()
			#print command
		#print command
	        
	    #s.send(" ")
    conn.send('Thank you for connecting')
    conn.close()

