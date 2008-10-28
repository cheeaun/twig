Element.implement({
	show: function() {
		if(this.hidden()) this.setStyle('display', '');
		return this;
	},
	hide: function() {
		if(!this.hidden()) this.setStyle('display', 'none');
		return this;
	},
	hidden: function() {
		return (this.getStyle('display') == 'none') ? true : false;
	}
});

window.addEvent('domready',function(){

	if($('twig-form')) {
		// countable for textarea
		new Countable("message",140,"counter");
		
		// submit button validation
		$('twig-form').onsubmit = function(){
			var c = $('counter').innerHTML.toInt();
			var m = $('message');
			var e = $('error');
			if(c>=140) {
				m.focus();
				e.hide()
				return false;
			}
			else if(c<0) {
				m.focus();
				e.show();
				(function(){ e.hide(); }).delay(15000);
				return false;
			}
			else e.hide();
		};
		
		// reply links
		$$('.reply').each(function(el){
			el.addEvent('click', function(e){
				e = new Event(e).stop();
				var u = this.getParent().getElements('.user a')[0].getText();
				var m = $('message');
				var t = m.value.clean();
				
				// smart @ appending (tm)
				if(!t.contains('@'+u))
					if(t.contains('@'))
						m.value = t + ' @' + u + ' ';
					else
						m.value = '@' + u + ' ' + t;
				
				m.focus();
			});
		});
		
		// AJAX request
		var urlreq;
		
		// short url link
		$('shorturl-link').addEvent('click', function(e){
			e = new Event(e).stop();
			var form = $('shorturl-form');
			var m = $('message');
			var t = $('shorturl-text');
			var err = $('shorturl-error');
			var b = $('shorturl-button');
			
			if(form.hidden()) {
				form.show();
				
				// smart URL detection (tm)
				var status = m.value.clean().split(' ').filter(function(s){
					return (s.test('^https?://'));
				});
				
				// find the longest URL
				if(status.length) {
					var url;
					var len = 25; // min 25 chars
					status.each(function(s){
						if(s.length>len){
							url = s;
							len = s.length;
						}
					});
					
					if(url) t.value = url;
				}
			
				t.focus();
			}
			else {
				t.value = '';
				form.hide();
				err.hide();
				if(urlreq) urlreq.cancel();
				m.focus();
			}
		});
		
		// shorturl button
		$('shorturl-button').addEvent('click', function(e){
			e = new Event(e).stop();
			var m = $('message');
			var t = $('shorturl-text');
			var err = $('shorturl-error');
			var b = $('shorturl-button');
			var loader = $('loader');
			
			// disable the textarea to prevent weird stuff
			m.disabled = true;
			b.disabled = true;
			
			// get URL
			var url = t.value.clean();
			
			// begin loader
			loader.show();
			
			// begin ajax stuff
			urlreq = new Request({
				url: '/_url',
				method: 'get',
				onSuccess: function(u) {
					if(u.contains('http')) {
						var mval = m.value.clean();
						if(!mval)
							m.value = u;
						else if(mval.contains(url))
							m.value = mval.split(url).join(u);
						else
							m.value = mval+' '+u;
							
						m.disabled = false;
						b.disabled = false;
						m.focus();
						
						t.value = '';
						err.hide();
						
						$('shorturl-form').hide();
						loader.hide();
					}
					else {
						m.disabled = false;
						b.disabled = false;
						err.show();
						loader.hide();
						t.focus();
					}
				},
				onFailure: function() {
					m.disabled = false;
					b.disabled = false;
					err.show();
					t.focus();
					loader.hide();
				},
				onCancel: function() {
					m.disabled = false;
					b.disabled = false;
					err.hide();
					loader.hide();
				}
			}).send('u='+url);
		});
	}

});