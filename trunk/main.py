#!/usr/bin/env python

import datetime
import wsgiref.handlers
import math
import re
import cgi

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import urlfetch

tpath = 'templates/'
page = {
	'main': tpath+'main.html',
	'user': tpath+'user.html',
	'status': tpath+'status.html',
	'search': tpath+'search.html',
	'htmlhead': 'htmlhead.html',
	'header': 'header.html',
	'footer': 'footer.html'
}

limit = 10
maxlimit = 100

class Twig(db.Model):
	message = db.StringProperty(required=True)
	when = db.DateTimeProperty(auto_now_add=True)
	who = db.StringProperty(required=True)
	tid = db.StringProperty(required=True)

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		errorurl = self.request.get('error')
		error = True if errorurl else False
		
		msg = self.request.get('t')
		
		if user:
			url = users.create_logout_url('/')
			url_linktext = 'Logout'
		else:
			url = users.create_login_url('/?t='+msg) if msg else users.create_login_url('/')
			url_linktext = 'Login or register'
			
		p = self.request.get('page')
		p = int(p) if p else 1
		offset = (p-1)*limit if p else 0
		
		twigs = db.GqlQuery('SELECT * FROM Twig ORDER by when DESC')
		pagenums = int(math.ceil(float(twigs.count())/limit))
		twigs = twigs.fetch(limit, offset)
		twigs = cleanTwigs(twigs)
#		for twig in twigs:
#			twig.delete()
		
		pagelinks = genPagelinks(p, pagenums)

		values = {
			'twigs': twigs,
			'user': user,
			'url': url,
			'url_linktext': url_linktext,
			'page': page,
			'error': error,
			'pagelinks': pagelinks,
			'msg': msg
		}
		
		self.response.out.write(template.render(page['main'], values))
		
	def post(self):
		dt = datetime.datetime.now()
		dt = str(dt).replace('-','').replace(' ','').replace(':','').replace('.','')
		
		msg = self.request.get('message')
		msg = msg.strip().replace('\n','').replace('\r',' ').replace('\t',' ')
		
		u = users.get_current_user()
		person = str(u)
		if not msg:
			self.redirect('/')
		elif len(msg) > 140:
			self.redirect('/?error=1')
		else:
			twig = Twig(
				message=msg,
				who=person,
				tid=dt
			)
			twig.put()
			self.redirect('/')

class UserPage(webapp.RequestHandler):
	def get(self, u):
		user = users.get_current_user()
		
		owner = True if (u == str(user)) else False
		
		if user:
			url = users.create_logout_url("/")
			url_linktext = 'Logout'
		else:
			url = users.create_login_url("/")
			url_linktext = 'Login or register now.'
			
		p = self.request.get('page')
		p = int(p) if p else 1
		offset = (p-1)*limit if p else 0

		twigs = db.GqlQuery('SELECT * FROM Twig WHERE who = :1 ORDER by when DESC', u)
		pagenums = int(math.ceil(float(twigs.count())/limit))
		twigs = twigs.fetch(limit, offset)
		twigs = cleanTwigs(twigs)
		
		ucode = unicode("\xEF\xBF\xBD", errors='replace')
		atwigs = db.GqlQuery('SELECT * FROM Twig WHERE message >= :1 AND message < :2', '@'+u, '@'+u+ucode)
		atwigs = atwigs.fetch(limit, offset)
		atwigs = cleanTwigs(atwigs)
		
		pagelinks = genPagelinks(p, pagenums)
		
		if owner:
			title = 'Your twigs'
		else:
			title = u + "'s twigs"

		values = {
			'user': user,
			'url': url,
			'url_linktext': url_linktext,
			'page': page,
			'owner': owner,
			'u': u,
			'title': title
		}
		
		if twigs: values['twigs'] = twigs
		if atwigs: values['atwigs'] = atwigs
		
		self.response.out.write(template.render(page['user'], values))
		
class StatusPage(webapp.RequestHandler):
	def get(self, u, tid):
		twigs = db.GqlQuery('SELECT * FROM Twig WHERE who = :1 AND tid = :2', u, tid)
		twigs = cleanTwigs(twigs)
		
		title = u + "'s twig"

		values = {
			'twigs': twigs,
			'page': page,
			'title': title
		}
		
		self.response.out.write(template.render(page['status'], values))

class ShortURLPage(webapp.RequestHandler):
	def get(self):
		u = self.request.get('u')
		if u:
			url = 'http://tinyurl.com/api-create.php?url='+str(u)
			result = urlfetch.fetch(url)
			if result.status_code == 200:
				self.response.out.write(result.content)

class SearchPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		q = self.request.get('q')
		
		if user:
			url = users.create_logout_url("/")
			url_linktext = 'Logout'
		else:
			url = users.create_login_url("/")
			url_linktext = 'Login or register now.'
			
		if q:
			ucode = unicode("\xEF\xBF\xBD", errors='replace')
			twigs = db.GqlQuery('SELECT * FROM Twig WHERE message >= :1 AND message < :2', q, q+ucode)
			twigs = cleanTwigs(twigs)
			
			title = 'Search &quot;'+q+'&quot;'

			values = {
				'twigs': twigs,
				'user': user,
				'url': url,
				'url_linktext': url_linktext,
				'page': page,
				'title': title
			}
		else:
			title = 'Search'
			values = {
				'user': user,
				'url': url,
				'url_linktext': url_linktext,
				'page': page,
				'title': title
			}
		
		self.response.out.write(template.render(page['search'], values))

def cleanTwigs(twigs):
	twigs2 = []
	for twig in twigs:
		msg = cgi.escape(twig.message, True)
		aliases = re.findall('\B@(\S+)', msg)
		if aliases:
			for a in aliases:
				msg = re.sub('@'+a, '@<a href="/'+a+'">'+a+'</a>', msg)
		twig.message = msg
		twigs2.append(twig)
	return twigs2

def genPagelinks(p, pagenums):
	pagelinks = ''
	if pagenums>1:
		pagelinks = '<p class="pagenums">'
		if p>1: pagelinks += '<a href="?page='+str(p-1)+'" title="Page '+str(p-1)+'">&larr; Newer</a> '
		for i in range(pagenums):
			selected = ' class="selected"' if (i+1) == p else ''
			i = str(i+1)
			pagelinks += '<a href="?page='+i+'" title="Page '+i+'"'+selected+'>'+i+'</a> '
		if p<pagenums: pagelinks += '<a href="?page='+str(p+1)+'" title="Page '+str(p+1)+'">Older &rarr;</a> '
		pagelinks += '</p>'
	return pagelinks

def main():
	app = webapp.WSGIApplication([
		('/', MainPage),
		('/_url', ShortURLPage),
		('/_search', SearchPage),
		(r'/([^/]*)', UserPage),
		(r'/([^/]*)/([^/]*)', StatusPage)
	], debug=True)
	wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
  main()
