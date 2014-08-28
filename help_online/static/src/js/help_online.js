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
    
    openerp.web.TreeView.include({
        view_loading: function(r) {
            var ret = this._super(r);
            if(! _.isUndefined(this.ViewManager.load_help_buttons)){
                this.ViewManager.load_help_buttons();
            }
            return ret
        },
    });
    
    openerp.web.ListView.include({
        view_loading: function(r) {
            var ret = this._super(r);
            if(! _.isUndefined(this.ViewManager.load_help_buttons)){
                this.ViewManager.load_help_buttons();
            }
            return ret
        },
    });
    
    openerp.web.FormView.include({
        view_loading: function(r) {
            var ret = this._super(r);
            if(!_.isUndefined(this.ViewManager.clean_help_buttons)){
                this.ViewManager.clean_help_buttons();
            }
            return ret
        },
        
        do_show: function (options){
            var ret = this._super(options);
            if(! _.isUndefined(this.ViewManager.load_help_buttons)){
                this.ViewManager.load_help_buttons();
            }
            return ret
        },
    });

    openerp.web.ViewManager.include({
        clean_help_buttons:function() {
            this.$el.find("div.oe_help_online_buttons").first().remove();
        },
        
        load_help_buttons:function() {
            var self = this;	
            this.rpc('/help_online/build_url',  {model: this.dataset.model, view_type: this.active_view}).then(function(result) {
                self.clean_help_buttons();
                if (result && ! _.isEmpty(result)) {
                    self.$helpButtonsEl = $(QWeb.render("HelpOnline.Buttons", {'view_manager':self, 'url_info': result}));
                    self.$el.find("ul.oe_view_manager_switch.oe_button_group.oe_right").first().before(self.$helpButtonsEl);
                    if (result.exists === false) {
                        self.$helpButtonsEl.find('li').addClass('oe_help_online_not_found')
                    
                    }
                    
                }
            });
        },

    });
}
