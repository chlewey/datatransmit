
from time import *
from requests import Session
import hashlib,json,myfile,debug
import sitrad

class API(Session):
	myID = 'me'
	passwd = None
	server = 'www.orugaamarilla.com'
	headers = {}

	def __init__(self):
		Session.__init__(self)
		self.headers = {
			"User-Agent": "Oruga Amarilla transmit API",
			"Content-type": "application/x-www-form-urlencoded",
			"Accept": "text/plain"
			}
		with myfile.db('config.mod',':') as p:
			for k in p:
				if k[0]=='base':
					self.myID = k[1]
					debug.out2('This site name',self.myID)
				elif k[0]=='remote':
					self.server = k[1]
					debug.out2('Sending to server',self.server)
				elif k[0]=='header':
					self.headers[k[1]] = k[2]
					debug.out2('Adding POST header','{}:{}'.format(k[1],k[2]))
				elif k[0] in {'interval','pause'}:
					self.interval = int(k[1])
					debug.out2('Interval set to',self.interval)
				elif k[0] in {'iters','repeat'}:
					i = int(k[1])
					self.repeat = int(i)
					if not i: i = 'infinity'
					debug.out2('Setting iterations to',i)
		self.auth = (self.myID,self.passwd)

	def request(self,method,uri='',**kwargs):
		self.r = Session.request(
			self=self,
			method=method,
			url='http://'+self.server+'/datalog/'+uri,
			**kwargs)

	def json(self):
		return self.r.json()

	def text(self):
		return self.r.text
	
	def status(self,textual=False):
		if textual:
			if 'status' in self.r.headers.keys():
				return self.r.headers['status']
		return self.r.status_code

class OrugaAPI(API):
	myID = 'me'
	passwd = None
	server = 'www.orugaamarilla.com'
	headers = {}
	
	def __init__(self):
		API.__init__(self)
		self.tick = time()
		self.interval = 10
		self.repeat = False
		self.san = int(self.tick)
		self.openHT()

	def openHT(self):
		return
		self.resource = '/datalog/{}.cgi'.format(self.myID)
		self.conn = HTTPConnection(self.server)

	def main(self,iters=None):
		if not iters: iters = self.repeat
		if iters:
			for i in range(iters):
				self.cycle()
				self.wait()
				debug.out('\n')
		else:
			while self.cycle():
				self.wait()

	def cycle(self):
		changes = {}
		with myfile.db('readers.mod') as r:
			for k in r:
				changes.update(self.read(k))
		with myfile.db('databases.mod') as d:
			for k in d:
				changes.update(self.check(k))
		self.transmit(changes)
		return True

	def wait(self,sec=None):
		if not sec and self.interval:
			sec = self.interval
		if sec:
			ts = (int(self.tick/sec)+1)*sec
			nt = time()
			if nt<ts:
				sleep(ts-nt)
			else: ts=nt
			debug.out(strftime("%Y-%m-%d (%a) %H:%M:%S",localtime(ts)))
			self.tick = ts

	def read(self,args):
		return {}

	def check(self,args):
		if not args:
			return {}
		if args[0] == 'sitrad':
			return sitrad.check(args[1],self.tick-31556952)
		debug.out('Undefined database {}.'.format(args[0]))
		return {}

	def transmit(self,changes):
		self.san += 543
		self.san *= 17
		self.san %= 2797
		clock = int(time()//300)
		rock = '[{:09}{:9}:{:4}]'.format(clock,self.myID,self.san)
		dic = {
			'from': self.myID,
			'R{:04}'.format(self.san): hashlib.md5(rock.encode('ascii')).hexdigest()
			}
		
		if(changes):
			debug.out2('Changes',', '.join(changes.keys())+'.')
			for (key,val) in changes.items():
				if type(val) in (type({}),type([])):
					debug.out2(key,val)
					dic[key] = json.dumps(val)
				else:
					dic[key] = val
			params = json.dumps(dic)
			prepar = 'O:'+params+':A'
			dic['sign'] = hashlib.md5(prepar.encode('ascii')).hexdigest()
			self.post('',data=dic)
			debug.out(self.status(True))
			if(self.status() >= 200):
				debug.out(self.text());
		else:
			debug.out('No changes.')
			self.get('',params=dic)
			debug.out(self.status(True))
			data = self.json()
			if(self.status() >= 200):
				debug.out(self.text());
