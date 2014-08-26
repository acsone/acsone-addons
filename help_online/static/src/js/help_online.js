openerp.help_online = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;

    instance.web.ListView.include({
        load_list: function () {
            var self = this;
            var add_button = false;
            if (!this.$buttons) {
                add_button = true;
            }
            this._super.apply(this, arguments);
            this.$buttons.on('click', '.oe_list_button_help_online', function() {
                self.do_action({
                    type: 'ir.actions.act_url',
                    url: '/partner_mobile',
                    target: 'self',
                });
            });
        },
    });

    openerp.web.ViewManager.include({
        start: function() {
            var self = this;
            this._super();
            this.load_help_buttons();
	    this.on('switch_mode', self, function(mode) {
                self.$el.find("ul#oe_help_buttons").remove()
            	self.load_help_buttons();
            });
        },

        load_help_buttons:function() {
            var self = this;
	    this.active_view_help_url = '/test/' + this.dataset.model + '?view_type=' + this.active_view;
            this.$ExpandButtons = $(QWeb.render("HelpOnline.Buttons", {'view_manager':self}));
            this.$el.find("ul.oe_view_manager_switch.oe_button_group.oe_right").before(this.$ExpandButtons);
        },

    });
}
