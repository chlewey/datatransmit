
import requests,sys

class theapi(requests.Session):
	def __init__(self,site,user,password=None):
		requests.Session.__init__(self)
		if not password:
			password = input('Password for {}: '.format(user))
		self.auth = (user,password)
		self.site = site

	def request(self,method,uri='',**kwargs):
		self.r = requests.Session.request(
			self=self,
			method=method,
			url='http://'+self.site+'/datalog/'+uri,
			**kwargs)

	def json(self):
		return self.r.json()

	def text(self):
		return self.r.text

def dir2str(d,t='',it='\t'):
	if type(d)==type(''):
		return '%s"%s"\n'%(it,d)
	if type(d)==type([]):
		s = t+'[\n'
		for v in d:
			s+= dir2str(v,t+'\t',t+it)
		s+= t+']\n'
		return s
	if type(d)==type({}):
		s = t+'{\n'
		for k in d.keys():
			v = d[k]
			s+= t+it+k+':'+dir2str(v,t+'\t')
		s+= t+'}\n'
		return s
	if type(d)==type(True):
		return '%s%s\n'%(t,d)
	if type(d)==type(None):
		return '\n'
	if type(d)==type(1):
		return '%s%d\n'%(t,d)
	if type(d)==type(1.0):
		return '%s%f\n'%(t,d)

if __name__ == "__main__":

	try:
		uri = sys.argv[1]
	except:
		uri = ''
	print("API Request is '{}'.".format(uri))
	try:
		user = sys.argv[2]
		print('User is {}.'.format(user))
	except:
		user = input('Please enter user: ')
		
	from siteconfig import *

	if user in passwd.keys():
		s = theapi(site,user,passwd[user])
	else:
		s = theapi(site,user)
	
	s.get(uri)
	print(s.text())
	try:
		print(dir2str(s.json()))
	except:
		pass
