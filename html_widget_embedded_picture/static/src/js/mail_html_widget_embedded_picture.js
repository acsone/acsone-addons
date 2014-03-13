/*
 * Add a button to html widget to insert 'unsubscribe' link
 */

var _t = openerp.web._t, _tl = openerp.web._tl;

openerp.html_widget_embedded_picture = function(instance) {

    var QWeb = instance.web.qweb, _t = instance.web._t;
    instance.web.form.FieldTextHtml
            .include({

                init : function() {
                    this._super.apply(this, arguments);
                },

                start : function() {
                    this._super.apply(this, arguments);
                    var self = this;
                    self.add_template_picture_loader();
                    self.focus_on_picture_loader();
                },

                openpopup : function(content){
                    var myWindow = window.open("","","width=200,height=100");
                    myWindow.document.write(content)
                },

                focus_on_picture_loader : function(){
                    var self = this;
                    $("#button_picture_loader").click(function() {
                        self.openpopup($(QWeb.render('form_picture_loader')).html());
                    });
                },

                insert_and_focus_picture : function(content) {
                    var self = this;
                    self.$cleditor.execCommand("inserthtml", contect);
                    self.$cleditor.focus();
                },

                add_template_picture_loader : function() {
                    $(".cleditorToolbar:last").find(".cleditorGroup").eq(-2)
                            .find(".cleditorDivider:last").parent().before(
                                    $(QWeb.render('template_picture_loader')));
                },

            });
}
