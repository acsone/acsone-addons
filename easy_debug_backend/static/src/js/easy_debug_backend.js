openerp.easy_debug_backend = function(instance) {

    instance.web.ActionManager.include({
        init : function() {
            this._super.apply(this, arguments);
        },
        do_action : function(action, options) {
            if (window.location.href.indexOf('debug') == -1) {
                window.location = $.param.querystring(window.location.href,
                        'debug');
            }
            return this._super.apply(this, arguments);
        }
    });

};
