/*
 * Allow to bypass readonly fi the value is changed
 */
openerp.readonly_bypass = function(instance) {

    var QWeb = instance.web.qweb, _t = instance.web._t;
    instance.web.DataSet.include({

        init : function() {
            this._super.apply(this, arguments);
        },
        /**
         * Creates Overriding
         *
         * @param {Object} data field values to set on the new record
         * @param {Object} options Dictionary that can contain the following keys:
         *   - readonly_fields: Values from readonly fields that were updated by
         *     on_changes. Only used by the BufferedDataSet to make the o2m work correctly.
         * @returns super {$.Deferred}
         */
        create : function(data, options) {
            var self = this;
            self.ignore_readonly(data, options);
            return self._super(data,options);
        },
        /**
         * Creates Overriding
         *
         * @param {Object} data field values to set on the new record
         * @param {Object} options Dictionary that can contain the following keys:
         *   - readonly_fields: Values from readonly fields that were updated by
         *     on_changes. Only used by the BufferedDataSet to make the o2m work correctly.
         * @returns super {$.Deferred}
         */
        write : function(id, data, options) {
            var self = this;
            self.ignore_readonly(data, options);
            return self._super(id,data,options);
        },
        /**
         * ignore readonly: place options['readonly_fields'] into the data
         * if nothing is specified into the context
         *
         *
         * @param {Object} data field values to possibly be updated
         * @param {Object} options Dictionary that can contain the following keys:
         *   - readonly_fields: Values from readonly fields to merge into the data object
         */
        ignore_readonly: function(data, options){
            var self = this;
            if (!('filter_out_readonly' in self.context && self.context['filter_out_readonly'] == true
                    && 'readonly_fields' in options && options['readonly_fields'])) {
                data = $.extend(data,options['readonly_fields'])
            }
        },

    });
};
