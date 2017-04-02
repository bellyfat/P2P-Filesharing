import socket
import hashlib
import time
import os
import sys
import threading
import shutil
cport = 12276
s = socket.socket()
host = ""
current_time = time.time()
timediff = 10
s.connect((host, cport))
allarg = sys.argv
if not os.path.exists(allarg[1]):
    os.makedirs(allarg[1])
os.chdir(allarg[1])
s.send("Hello server!")
def receive_data_udp(filename,input,connection):
    port = int(cport)+11
    sock_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock_udp.bind((host,port))
    addr = (host,port)
    buf = 10240

    f = open(filename,'wb')
    connection.send(input)
    data,addr = sock_udp.recvfrom(buf)
    try:
        while(data):
            f.write(data)
            sock_udp.settimeout(2)
            data,addr = sock_udp.recvfrom(buf)
    except socket.timeout:
        f.close()
        sock_udp.close()
        print 'File Downloaded via UDP protocol'
def file_permission(number,file):
    try:
        permission = number[4:7]
        number =0
        octal = 1
        for i in range(0,3):
            number += octal * int(permission[2-i])
            octal *= 8
        os.chmod(file,number)
    except Exception as e:
        print(e)  
def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
def recursive_sync():
    conn.send("filenames")
    u = conn.recv(1024)
    y = u.split()
    leng = len(y)/3
    allfiles = os.listdir('.')
    for file in allfiles:
        try:
            if not os.path.isdir(file):
                test = 0
                for g in range(0,leng):
                    if y[3*g] == file:
                        test = 1
                if test == 0:
                    os.unlink(file)
            if os.path.isdir(file):
                test = 0
                for g in range(0,leng):
                    if y[3*g] == file:
                        test = 1
                if test == 0:
                    shutil.rmtree(file)
        except Exception as e:
            print(e)
    for g in range(0,leng):
        p = y[3*g]
        mtime = 0
        if os.path.exists(p) and os.path.isdir(p):
            mtime = os.path.getmtime(p)
            conn.send("chdir "+p)
            conn.recv(1024)
            os.chdir(p)
            recursive_sync()
            os.chdir("..")
            conn.send("chdir ..")
            conn.recv(1024)
        elif not os.path.exists(p) and y[3*g+2] == "dir":
            os.makedirs(p)
            conn.send("chdir "+p)
            conn.recv(1024)
            os.chdir(p)
            recursive_sync()
            os.chdir("..")
            conn.send("chdir ..")
            conn.recv(1024)
        else:
            if os.path.exists(p):
                mtime = os.path.getmtime(p)
            if float(mtime) < float(y[3*g+1]): 
                conn.send("copy "+str(p))
                string = ""
                try:
                    while True:
                        conn.settimeout(0.1)
                        u = conn.recv(1024)
                        e = u.split(" ")
                        if not u or not len(e):
                            break
                        string += u
                except socket.timeout:
                    if p:
                        try: 
                            open(p,'wb')
                        except:
                            os.unlink(p)
                        with open(p,'wb') as file:
                            file.write(string)
                        conn.send("filepermission "+str(p))
                        u = conn.recv(1024)
                        file_permission(u,str(p))
    return
def sync():
    timediff = 10
    while(True):
        if timediff > 5:
            current_time = time.time()
            recursive_sync()
        timediff = (time.time() - current_time)
    return
while True:
    conn = s   
    print ("prompt>"),
    d = raw_input()
    print ""
    arr = d.split(' ')
    currdir = '.'
    if arr[0] == "download":
        if arr[1] == "TCP":
            conn.send(d)
            print('Sent ',repr(d))
            print('Done sending')
            string = ""
            try:
                while True:
                    conn.settimeout(0.1)
                    u = conn.recv(1024)
                    if not u:
                        break
                    string += u
            except socket.timeout:
                with open(arr[2] + '_tcp','wb') as file:
                    file.write(string)
        elif arr[1] == "UDP":
            receive_data_udp(arr[2] + '_udp',d,conn)
        conn.send("downloadedinfo"+" "+arr[2])
        u = conn.recv(1024)
        print u
        if arr[1] == "UDP":
            conn.send("md5hash"+" "+arr[2])
            u = conn.recv(1024)
            u = u.split(' ')[0]
            if str(md5(arr[2]+'_udp')) == str(u):
                print "hash verification successful"
            else:
                print "hash verification unsuccessful"
        conn.send("filepermission "+arr[2])
        u = conn.recv(1024)
        if arr[1] == "TCP":
            file_permission(u,arr[2]+'_tcp')
        else:
            file_permission(u,arr[2]+'_udp')
    elif arr[0] == "sync":
        try:
            r = threading.Thread(target=sync)
            r.start()
        except:
            print "unable to start thread"
    else:
        conn.send(d)
        u = conn.recv(1024)
        print u
    

