openerp.distribution_list = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.distribution_list = instance.web.distribution_list || {};

    instance.web.views.add('tree_selection',
            'instance.web.distribution_list.FilterSelection');

    instance.web.distribution_list.FilterSelection = instance.web.ListView
            .extend({
                init : function() {
                    this._super.apply(this, arguments);
                    //This option provides a way to hide the select box
                    //into the list view
                    this.options.selectable = false;
                },
                start : function() {
                    var tmp = this._super.apply(this, arguments);
                    var self = this;
                    //Add the QWebto the view
                    this.$el.parent().prepend(QWeb.render("FilterSelection", {
                        widget : this
                    }));
                    this.$el.parent().find('.oe_deamon_active_domain').on(
                            'click', function(item) {
                                self.on_action_clicked(item);
                            });
                    return tmp;
                },

                on_action_clicked : function(item) {
                    /*
                     * pre: item is initialized and contain the item clicked
                     * post: the view is closed
                     * res: the 'save_domain' method is called from the model
                     *      'distribution.list.line'
                     */
                    var self = this;
                    var model = new instance.web.Model(
                            "distribution.list.line", self.dataset.context,
                            self.dataset.domain);
                    model.call(
                            "save_domain",
                            [ this.dataset.context['res_id'][0],
                                    this.dataset.get_domain() ], {
                                context : new instance.web.CompoundContext()
                            }).then(function(result) {
                        self.do_action({
                            "type" : "ir.actions.act_window_close"
                        });
                    });
                },
            });
};
