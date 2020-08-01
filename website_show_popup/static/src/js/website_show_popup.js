odoo.define('website_show_popup', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var websiteRootData = require('website.WebsiteRoot');
    
    var WebsiteShowPopup = Widget.extend({

        start: function () {
            var self = this;
            var repr = $('html').data('main-object-popup');
            var m = repr.match(/(.+)\((\d+),(.*)\)/);
            
            var model =  m[1];
            var page_id =  m[2] | 0;

            if (model && page_id) {
                self._rpc({
                    route: '/website/website_show_popup',
                    params: {
                        'model': model,
                        'page_id': page_id,
                    },
                }).then(function (result) {   
                    var popup_html = '';
                    var popup_title_html = '';
                    if (result){                        
                        popup_title_html += result['title'];
                        popup_html += result['popup'];
                        var popup ='<div class="modal" id="cf_website_popup" role="dialog">' +
                                    '<div class="modal-dialog">' +
                                        '<div class="modal-content">' +
                                            '<div class="modal-header">' +
                                                '<h4 class="modal-title" id="cf_website_popup_close_title">'+ popup_title_html +'</h4>' +
                                                '<button type="button" id="cf_website_popup_close_header" class="close" data-dismiss="modal">&times;</button>' +                                            
                                            '</div>' +
                                            '<div class="modal-body" id="cf_website_popup_content">' + popup_html + '</div>' +
                                        '</div>' +
                                    '</div>' +
                                '</div>' ;
                        $("body").prepend(popup);
                        $('#cf_website_popup').show();

                        $("#cf_website_popup_close_header").mouseup(function(ev) {                 
                            $('#cf_website_popup').hide();
                        });

                    }
                });
            }
            
            return this._super.apply(this, arguments);
        },

    })
    websiteRootData.websiteRootRegistry.add(WebsiteShowPopup, '#wrapwrap');
    return WebsiteShowPopup;

});