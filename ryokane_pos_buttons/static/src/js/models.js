odoo.define("ryokane_pos_buttons.models", function(require) {
    "use strict";

    var rpc = require('web.rpc');
    var session = require("web.session");
    var models = require("point_of_sale.models");
    var screens = require("point_of_sale.screens");

    var productModelIndex = _.findIndex(models.PosModel.prototype.models, { model: 'res.partner' });
    models.PosModel.prototype.models[productModelIndex] = {
        model: 'res.partner',
        fields: ['name', 'street', 'city', 'state_id', 'country_id', 'vat',
            'phone', 'zip', 'mobile', 'email', 'barcode', 'write_date',
            'property_account_position_id', 'property_product_pricelist', 'company_type'
        ],
        domain: [
            ['customer', '=', true],
            ['hcategory_id.id', '=', 10]
        ],
        loaded: function(self, partners) {
            partners = _.filter(partners, function(partner) {
                return partner.company_type == 'person';
            });
            self.partners = partners;
            self.db.add_partners(partners);
        },
    }

    screens.PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            var order = this.pos.get_order();
            // order.practitioner && order.reservation && order.salesperson
            if (true) {
                if (this.order_is_valid(force_validation)) {
                    this.finalize_validation();
                }
                $('span.reservation').text("Reservation Source");
                $('span.salesperson').text("Sale Person");
                $('span.practitioner').text("Practitioner");

            }else{
                this.gui.show_popup("error", {
                    title: "Practitioner and Reservation",
                    body: "practitioner and reservation is not selected"
                });
            }

        },

    });

    models.PosModel = models.PosModel.extend({

        load_new_partners: function() {
            var self = this;
            var def = new $.Deferred();
            var fields = _.find(this.models, function(model) { return model.model === 'res.partner'; }).fields;
            var domain = [
                ['customer', '=', true],
                ['hcategory_id.id', '=', 10],
                ['write_date', '>', this.db.get_partner_write_date()]
            ];
            rpc.query({
                    model: 'res.partner',
                    method: 'search_read',
                    args: [domain, fields],
                }, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function(partners) {
                    partners = _.filter(partners, function(partner) {
                        return partner.company_type == 'person';
                    });
                    if (self.db.add_partners(partners)) { // check if the partners we got were real updates
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function(type, err) { def.reject(); });
            return def;
        },


        get_lot: function(product, location_id) {
            var done = new $.Deferred();
            session.rpc("/web/dataset/search_read", {
                "model": "stock.production.lot",
                "domain": [

                    ["product_id", "=", product]
                ]
            }, { 'async': false }).then(function(result) {
                var product_lot = {};
                if (result.length) {
                    for (var i = 0; i < result.length; i++) {
                        if (product_lot[result.records[i].id]) {
                            product_lot[result.records[i].name] += result.records[i].quantity;
                        } else {
                            if (result.records[i].product_qty > 0) {

                                product_lot[result.records[i].name] = result.records[i].quantity;
                            }
                        }

                    }
                }
                done.resolve(product_lot);
            });
            return done;
        },
    });

    var _orderline_super = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        compute_lot_lines: function() {
            var done = new $.Deferred();
            var compute_lot_lines = _orderline_super.compute_lot_lines.apply(this, arguments);
            this.pos.get_lot(this.product.id, this.pos.config.stock_location_id[0])
                .then(function(product_lot) {
                    var lot_name = Object.keys(product_lot);
                    for (var i = 0; i < lot_name.length; i++) {
                        if (product_lot[lot_name[i]] < compute_lot_lines.order_line.quantity) {
                            lot_name.splice(i, 1);
                        }
                    }
                    compute_lot_lines.lot_name = lot_name;
                    done.resolve(compute_lot_lines);
                });
            return compute_lot_lines;
        },
    });

});