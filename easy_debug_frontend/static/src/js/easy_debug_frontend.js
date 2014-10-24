(function() {
    'use strict';

    var website = openerp.website;
    var _t = openerp._t;
    var _super_website_ready = website.ready;

    website.ready = function(options) {
        if (window.location.href.indexOf('debug') == -1) {
            window.location = $.param
                    .querystring(window.location.href, 'debug');
        }
        return _super_website_ready();
    }
})();
