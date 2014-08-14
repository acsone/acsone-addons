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
}
