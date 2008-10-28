var Countable = new Class({
 
	initialize: function(inputId, max, counterId, errorClass) {
	 
		this.input = $(inputId);
		this.max = max;
		this.errorClass = errorClass ? errorClass : "error";
	 
		this.handle = $(counterId);

		this.input.addEvent('keydown', this.onKeyPress.bindWithEvent(this));
		this.input.addEvent('keyup', this.onKeyPress.bindWithEvent(this));
		this.input.addEvent('click', this.onKeyPress.bindWithEvent(this));
		this.input.addEvent('blur', this.onKeyPress.bindWithEvent(this));
		this.input.addEvent('focus', this.onKeyPress.bindWithEvent(this));
		this.update();
 
	},
 
	onKeyPress: function(event) {
		event = new Event(event);
		if(!event.shift && !event.control && !event.alt && !event.meta) this.update();
	},

	update: function() {
 
//		if (this.input.value.length > this.max)
//			this.input.value = this.input.value.substring(0, this.max);

		var val = this.input.value.replace('\n',' ');
 
		var count = this.max - this.input.value.length;
	  
		if(count<=10) this.handle.addClass(this.errorClass);
		else this.handle.removeClass(this.errorClass);
 
		this.handle.set('text', count);
	}
 
});