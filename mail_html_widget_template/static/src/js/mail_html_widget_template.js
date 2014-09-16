/*
 * Add selection for placeholder in html widget
 */
openerp.mail_html_widget_template = function(instance) {

    var QWeb = instance.web.qweb, _t = instance.web._t;
    instance.web.form.FieldTextHtml
            .include({
                init : function() {
                    /*
                     * res: last_level initialized with -1 call the
                     * super init
                     */
                    this._super.apply(this, arguments);
                    this.read_mode_template = false;
                    this.last_level = -1;
                    var context = this.getParent().dataset.context;
                    this.comment = context["comment"];
                    if (this.comment == undefined){
                        this.comment = false;
                    }
                    if (context.default_model == undefined) {
                        this.model_starter = context.model;
                    }
                    if (!this.model_starter) {
                        this.model_starter = context.active_model;
                    }
                    if (!this.model_starter) {
                        this.model_starter = context.default_model;
                    }
                    this.excluded_types = [ "many2many", "one2many",
                            "boolean", "selection", "related" ];
                    this.excluded_fields = [ "single_token", ".id" ];// rapid
                },
                start : function() {
                    /*
                     * pre: current instance is initialized
                     * post:/
                     * res: instance is started with the customized added
                     */
                    this._super.apply(this, arguments);
                    var self = this;
                    if (!this.model_starter) {
                        model_starter = self.get_model_starter();
                    }
                    else{
                        self.launch(true);
                    }
                },

                launch : function(trigger){
                    var self = this;
                    var show = true;
                    if(self.getParent().dataset.context.show != undefined){
                        show = self.getParent().dataset.context.show;
                    }
                    if(trigger && (!this.get("effective_readonly")) && show){
                        /*
                         * The select box is showed only if a context value is
                         * allowed depending on "this.where_to_show"
                         * Context could be altered if the page is
                         * reload by example:
                         * "Save as new template" from mass mailing will remove
                         * the default value into the context. It is necessary
                         * to keep consistency into the new reloaded window
                         */
                        self.getParent().dataset.context['show_reload'] = true;
                        self.on_focus_window();
                        self.add_selectbox_toolbar();
                        self.on_focus_checkbox('#' + this.last_level, this.$el);
                        self.load_record_fields(self.model_starter, false,
                                false);
                        try{
                            self.$cleditor.focus();
                        }
                        catch(err)
                        {
                            console.log(err);
                        }
                    }
                },

                get_model_starter : function() {
                    /*
                     * Try to get the starter model
                     * First check the model. If email.template then take it
                     * Otherwise search it into the context
                     */
                    var self = this;
                    if (self.getParent().model == 'email.template'){
                        //take the model_id
                        model = new instance.web.Model(self.getParent().fields.model_id.field.relation);
                        model_id = self.getParent().fields.model_id.display_value;
                        if(Object.keys(model_id).length > 0){
                            model_id = parseInt($.map(model_id, function(key, value) { return value }));
                        }
                        else{
                            model_id = self.getParent().dataset.context.default_model_id
                        }
                        if(model_id == undefined){
                            self.launch(false);
                        }
                        else{
                            model.call('read',{ids: model_id,
                                               fields: ['model']}).then(function(result){
                               self.model_starter = result['model'];
                               self.launch(true);
                            });
                        }
                    }
                    else{
                        //take view model
                        self.model_starter = self.getParent().model;
                        self.launch(true);
                    }
                },

                on_focus_window : function() {
                    /*
                     * res: window is automatically focus when
                     * resized
                     */
                    var self = this;
                    $(
                            ".ui-dialog.ui-widget.ui-widget-content.ui-corner-all.oe_act_window.ui-draggable.ui-resizable.openerp")
                            .on('resize', function() {
                                try{
                                    self.$cleditor.focus();
                                }
                                catch(err){
                                    console.log(err);
                                }   
                            });
                },

                append_check_box : function(parent_value, records) {
                    /*
                     * pre : parent_value is a string and contains the value of
                     *     the parent fields records is a list of object
                     * records[N].value contains the value of the N child post
                     * a combo box is added in append to the tool-bar
                     */
                    var self = this;
                    self.add_selectbox_toolbar();

                    _.each(records, function(el) {
                        el.value = parent_value + "." + el.value;
                        self.load_option(el);
                    });

                    self.on_focus_checkbox('#' + this.last_level, this.$el);
                },

                on_focus_checkbox : function(id_check_box) {
                    /*
                     * pre: id_check_box is initialized with the id of an
                     *      element into the popup view.
                     * type: string . Ex: "#1"
                     * post: event on "change" is added on the element with id
                     * 'id_check_box'
                     * All the combo box with an id greater than the
                     *     id_check_box are removed from the tool bar.
                     */
                    var self = this;
                    $(id_check_box, this.$el)
                            .on(
                                    'change',
                                    function() {
                                        //4 because it is the max noticed into html mode
                                        if ($('.cleditorButton[disabled="disabled"]', this.$el).length <= 4){
                                            // do nothing if no value
                                            self.remove_check_box(this.id);
                                            if (this.value !== "") {
                                                // deserialize the string into an
                                                // object
                                                var object = JSON.parse(this.value);
    
                                                // assure that the type is allowed
                                                if (object.field_type !== "many2one") {
                                                    // insert the value into the
                                                    // textarea
                                                    // case where the mode is
                                                    // "comment" then put the real
                                                    // value
                                                    if (this.comment)
                                                        self
                                                                .set_real_value(object.value);
                                                    else
                                                        self
                                                                .insert_and_focus(
                                                                        object.value,
                                                                        false);
    
                                                } else {
                                                    // get the parent value
                                                    parent_value = object.value
                                                            .split('/')[0];
                                                    self.load_record_fields(
                                                            object.params.model,
                                                            true, parent_value);
                                                }
                                            }
                                        }
                                        else{
                                            alert('Placeholders have been disabled in html view');
                                            $('#'+self.last_level, this.$el).val("");
                                        }
                                    });
                },

                set_real_value : function(expr) {
                    /*
                     * pre: expr contains the value to translate into a real
                     *     value. 
                     * res: the real value of 'expr' is showed into the
                     *     html widget
                     */
                    var self = this;
                    var dataset = self.getParent().dataset;
                    var context = dataset.context;
                    if (context['default_res_id'] == undefined) {
                        var composer = new instance.web.Model(
                                "mail.compose.message");
                        composer
                                .query([ 'res_id', 'model' ])
                                .filter([ [ 'id', '=', context['active_id'] ] ])
                                .all()
                                .then(
                                        function(result) {
                                            obj = result[0];
                                            self
                                                    .set_value_from_placeholder(
                                                            obj.res_id,
                                                            obj.model, expr);
                                        });
                    } else {
                        self.set_value_from_placeholder(
                                context['default_res_id'],
                                context['default_model'], expr);
                    }
                },

                set_value_from_placeholder : function(record_id, dest_model,
                        expr){
                /*
                 * pre: record_id is the id of the record to get its data
                 *     dest_model is the model of the record_id expr is the
                 *     placeholder to evaluate
                 * post: insert the value of the record into the text area
                 */
                    var self = this;
                    var value = "object." + expr;
                    var model = new instance.web.Model("mail.compose.message",
                            self.getParent().dataset.context,
                            self.getParent().dataset.domain);
                    model.call("get_value_from_placeholder",
                            [ record_id, dest_model, value ], {
                                context : new instance.web.CompoundContext()
                            }).then(function(result) {
                        console.log(result);
                        self.insert_and_focus("" + result, true);
                    });
                },

                insert_and_focus : function(value, evaluated) {
                    /*
                     * pre: value is the value to insert into the text area of
                     *    the cleditor
                     *    evaluated is false if the value have to be insert with
                     *        the '${object.value or ''} else, inserted as it is
                     * post: value is inserted as placeholder into the textarea
                     * 
                     * Note: as placeholder or as evaluated placeholder
                     */
                    var self = this;
                    if (evaluated == false) {
                        if (value.indexOf("|safe") > -1)
                            value = "${(object." + value.replace('|safe','') + " or '')|safe}";
                        else
                            value = "${object." + value + " or ''}";
                    }
                    self.$cleditor.execCommand("inserthtml", value);
                    try{
                        self.$cleditor.focus();
                    }
                    catch(err){
                        console.log(err);
                    }
                    $('#'+self.last_level, this.$el).val("");
                },

                load_option : function(field) {
                    /*
                     * pre: field is initialized and is a field object
                     *     field.id: the technical name of the field
                     *     field.string is the interface name of the field
                     *     field.field_type is the type of the field
                     * post: field is added as option of the last combo-box
                     *     (last_id)
                     */
                    var self = this;
                    if (field.field_type == "html")
                        field.value = field.value + '|safe';
                    var json_text = JSON.stringify(field, null, 2);
                    if (self.is_field_allowed(field.field_type) == true
                            && self.excluded_fields_to_show(field.id) == false){
                        $("#" + self.last_level, this.$el).append(
                                $('<option title=\'' + field.string + '\' id="'
                                        + field.id + '" value=\'' + json_text
                                        + '\'>'
                                        + self.get_fixed_max_size(field.string)
                                        + '</option>'));
                    }
                },

                get_fixed_max_size : function(value) {
                    /*
                     * :param value: value is initialized
                     * :rparam: 10 first value's character with '...' in the end
                     * if sizeof value > 10 else return value :rtype: char
                     * 
                     * This method is used to get a safe and uniform combo-box
                     * length
                     */
                    if (value.length > 16) {
                        return value.substr(0, 10) + '...';
                    } else
                        return value;
                },

                load_record_fields : function(model, is_rec, rec_value) {
                    /*
                     * pre: all parameters are initialize
                     *    'model': the model to get the field
                     *    'is_rec': in case of recursion
                     *    'rec_value': the value to pass into the recursion mode
                     * post: case of recursion: add new check box with fields
                     *      of the model else load directly the fields into
                     *      the current box
                     */
                    var self = this;
                    // call the python method on model --> get the fields list
                    self.rpc("/web/export/get_fields", {
                        model : model,
                        import_compat : false,
                    }).done(function(records) {
                        if (is_rec === true) {
                            self.append_check_box(rec_value, records);
                        } else {
                            _.each(records, function(field) {
                                self.load_option(field);
                            });
                        }
                    });
                },

                remove_check_box : function(level) {
                    /*
                     * remove all select box with a greater level than
                     * 'level'
                     */
                    var self = this;
                    var t_temp = $(".oe_model_field_selector", this.$el);
                    for (i = 0; i < t_temp.length; i++) {
                        if (parseInt(t_temp[i].id) > parseInt(level)) {
                            $("select", this.$el).remove('#' + t_temp[i].id);
                            self.last_level--;
                        }
                    }
                },

                add_selectbox_toolbar : function() {
                    /*
                     * post: new combo box is added to tool-bar
                     * 
                     * If last_level is 0 then first add of combo-box
                     * Otherwise add it after the last added combo-box
                     */
                    var self = this;
                    current_level = self.last_level;
                    self.last_level++;
                    if (self.last_level == 0) {
                        $(".cleditorToolbar", this.$el).eq(-1).after(
                                $(QWeb.render("SelectorToolbar")));
                        $("#selector_toolbar", this.$el).append(
                                $(QWeb.render('ModelFieldsSelection')));
                    } else {
                        $("#" + current_level, this.$el).after(
                                $(QWeb.render('ModelFieldsSelection')));
                    }
                    $("#new_select", this.$el).attr('id', self.last_level);
                    try{
                        self.$cleditor.focus();
                    }
                    catch(err)
                    {
                        console.log(err);
                    }
                },

                is_field_allowed : function(field_type) {
                    /*
                     * True if the type of field is allowed
                     * False otherwise
                     */
                    var self = this;
                    var allowed = true;
                    for (i = 0; i < self.excluded_types.length; i++) {
                        if (field_type == self.excluded_types[i]) {
                            allowed = false;
                            break;
                        }
                    }
                    return allowed;
                },

                excluded_fields_to_show : function(field_name) {
                    /*
                     * pre: field_name (string)
                     *     name of a field
                     * res: boolean depending if the field_name has to be shown
                     *      or not
                     */
                    var self = this;
                    var not_recommended = false;
                    for (i = 0; i < self.excluded_fields.length; i++) {
                        if (field_name == self.excluded_fields[i]) {
                            not_recommended = true;
                            break;
                        }
                    }
                    return not_recommended;
                },

                render_value: function() {
                    var self = this;
                    self._super();
                    if (! this.get("effective_readonly")) {
                        if(this.read_mode_template){
                            this.launch(true);
                            this.read_mode_template=false;
                        }
                    } else {
                        this.last_level = -1;
                        this.read_mode_template = true;
                    }
                },

            });
};
