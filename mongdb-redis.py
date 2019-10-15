#coding=utf-8
import pymongo
import redis
import time
import sys
import threading
import Queue

q=Queue.Queue()

class myThread (threading.Thread):
    def __init__(self,func,args1,args2):
        threading.Thread.__init__(self)
        self.func = func 
        self.args1 = args1
        self.args2 = args2
    def run(self):
        self.func(self.args1, self.args2)

def ip2num(ip):
    ip=[int(x) for x in ip.split('.')]
    return ip[0] <<24 | ip[1]<<16 | ip[2]<<8 |ip[3]
def num2ip(num):
    return '%s.%s.%s.%s' %( (num & 0xff000000) >>24,
                            (num & 0x00ff0000) >>16,
                            (num & 0x0000ff00) >>8,
                            num & 0x000000ff )
def get_ip(ip):
    start,end = [ip2num(x) for x in ip.split('-') ]
    return [ num2ip(num) for num in range(start,end+1) if num & 0xff ]

def mongo(q,f):
	while True:
		if not q.empty():
			ip=q.get()
			try:
				print ip.strip()+"\r"
				conn=pymongo.Connection(ip.strip(),27017)
				db = conn.database_names()
				if db:
					time.sleep(0.1)
					f.write(ip.replace("\n","\t")+"Login mongodb"+'\n')
					f.flush()
					print ip.replace("\n","\t")+"Login mongodb"+'\n'
				else:
					pass
				r=redis.Redis(host=ip,port=6379,db=0)
				rs=r.info()
				if rs:
					time.sleep(0.1)
					f.write(ip.replace("\n","\t")+"Login redis"+'\n')
					f.flush()
					print ip.replace("\n","\t")+"Login redis"+'\n'
				else:
					pass
			except:
				pass


if __name__ == '__main__':
	help_l=u"""
			Mongodbscan扫描
			   作者：沦沦
用法：
批量扫描：Mongodbscan.py -m 100 -u ip.txt url.txt
IP段扫描：Mongodbscan.py -m 100 -g 192.168.1.1-192.168.1.254 url.txt
	"""
	if len(sys.argv)<2:
		print help_l
	else:
		if len(sys.argv)>2:
			if sys.argv[1]=='-m':
				threads = []
				threadList = range(int(sys.argv[2]))
			if sys.argv[3]=='-u':
				ipc=open(sys.argv[4],"r")
				f=open(sys.argv[5],"w")
				for ipcc in ipc:
					q.put(ipcc)
				for i in threadList:
					t = myThread(mongo, q, f)
					t.setDaemon(True)
					threads.append(t)
					t.start()
				for t in threads:
					t.join()
			if sys.argv[3]=='-g':
				users = get_ip(sys.argv[4])
				f=open(sys.argv[5],"w")
				for user in users:
					q.put(user.strip())
				for i in threadList:
					t = myThread(mongo, q, f)
					t.setDaemon(True)
					threads.append(t)
					t.start()
				for t in threads:
					t.join()
