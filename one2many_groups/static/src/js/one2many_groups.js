openerp.one2many_groups = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt,
        QWeb = instance.web.qweb;

    instance.web.form.One2ManyListView.include({
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            this._super.apply(this, arguments);
        },
        view_loading: function(r) {
            var self=this;
            res = this._super.apply(this, arguments);
            $('.oe_add_group').bind('click', function(e){
                self.add_group(e.target.id);
            });
            return res;
        },
        add_group : function(level_id){
            var self = this;
            $('#'+level_id)
            $(this.el).find('thead').prepend(QWeb.render('group_row'));
        },

    });
}