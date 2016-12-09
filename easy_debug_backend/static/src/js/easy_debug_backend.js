odoo.define('easy_debug_backend.debug', function(require) {
    'use strict';
    var ActionManager = require('web.ActionManager');
    ActionManager.include({
        init : function() {            
            if (window.location.href.indexOf('debug') == -1){
                window.location = $.param.querystring(
                   window.location.href, 'debug=assets');
            }
            this._super.apply(this, arguments);
        },
    });

});
