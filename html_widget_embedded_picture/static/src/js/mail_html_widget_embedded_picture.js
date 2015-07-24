/*
 * Add a button to html widget to insert embedded picture into the html widget
 */

var _t = openerp.web._t, _tl = openerp.web._tl;

openerp.html_widget_embedded_picture = function(instance) {

    var QWeb = instance.web.qweb, _t = instance.web._t;
    instance.web.form.FieldTextHtml
            .include({

                init : function() {
                    this.read_mode_embedded=false;
                    this._super.apply(this, arguments);
                },

                start : function() {
                    this._super.apply(this, arguments);
                    var self = this;
                    if (! this.get("effective_readonly")) {
                        self.launch_embedded();
                    }
                },

                launch_embedded : function(){
                    var self = this;
                    self.add_template_picture_loader();
                    self.focus_on_picture_loader();
                },

                focus_on_picture_loader : function(){
                    var self = this;
                    $("#button_picture_loader", this.$el).click(function() {
                        //<2 because at least two
                        if ($('.cleditorButton[disabled="disabled"]', this.$el).length < 3){
                            var dlg = $(QWeb.render('template_form_picture_loader')).dialog({
                                resizable: false,
                                title: _t('Load Picture'),
                                modal: true,
                                appendTo: ".modal-content",
                            });
                            var dlg= new instance.web.Dialog(this, {
                                title: _t('Load Picture'),
                            }, $(QWeb.render('template_form_picture_loader'))).open();
                            $("button.cancelfilepicker", this.$el).click(
                                    function(event){
                                        $(dlg).dialog('close');
                            });
                            $("button.filepicker", this.$el).click(
                                    function(event){
                                        self.file_selection(dlg.el);
                            });
                        }
                    });
                },
                file_selection: function (dialog) {
                    /*
                     * generate a function for the post form answer allowing to insert
                     * a file from a local selection
                     */
                    var dlg = dialog;
                    var self = this;
                    var callback = _.uniqueId('func_');
                    $('input[name=func]', dialog).val(callback);

                    window[callback] = function (url, error) {
                        delete window[callback];
                        self.file_selected(url, error, dlg);
                    };
                    dialog.submit();
                },

                file_selected: function(url, error, dialog) {
                    /*
                     * img: image to be inserted
                     * error: possible error message
                     * dialog: reference to the open dialog
                     */
                    var self = this;
                    var $button = this.$('button.filepicker');
                    if (!error) {
                        self.insert_and_focus_picture(url);
                        $(dialog).dialog('close');
                    } else {
                        url = null;
                        this.$('form').addClass('has-error')
                            .find('.help-block').text(error);
                        $button.addClass('btn-danger');
                    }
                },

                insert_and_focus_picture : function(content) {
                    /*
                     * pre: content is initialized
                     * post: content is insert into the 'cleditor' text area
                     */
                    content = '<img src="' + content + '">';
                    var self = this;
                    self.$cleditor.execCommand("inserthtml", content);
                    try{
                        self.$cleditor.focus();
                    }
                    catch(err){
                        console.log(err);
                    }
                },

                add_template_picture_loader : function() {
                    /*
                     * Add qweb to the cleditor toolbar
                     */
                    $('.cleditorDivider:last').parent().before($(QWeb.render('template_button_picture_loader')));
                },

                render_value: function() {
                    var self = this;
                    self._super();
                    if (! this.get("effective_readonly")) {
                        if(this.read_mode_embedded){
                            self.launch_embedded();
                            this.read_mode_embedded=false;
                        }
                    } else {
                        this.read_mode_embedded = true;
                    }
                },

            });
}
