openerp.htmk_report_customization = function (instance) {
	module = instance.point_of_sale;
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	var fetch = function(model, fields, domain, ctx){
        return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
    };
    
	module.PosModel = module.PosModel.extend({
	load_server_data: function(){
            var self = this;

            var loaded = self.fetch('res.users',['name','company_id','email'],[['id','=',this.session.uid]]) 
                .then(function(users){
                    self.set('user',users[0]);

                    return self.fetch('res.company',
                    [
                        'currency_id',
                        'email',
                        'website',
                        'company_registry',
                        'vat',
                        'name',
                        'phone',
                        'partner_id',
                        'logo',
                    ],
                    [['id','=',users[0].company_id[0]]]);
                }).then(function(companies){
                    self.set('company',companies[0]);

                    return self.fetch('res.partner',['contact_address'],[['id','=',companies[0].partner_id[0]]]);
                }).then(function(company_partners){
                    self.get('company').contact_address = company_partners[0].contact_address;

                    return self.fetch('product.uom', null, null);
                }).then(function(units){
                    self.set('units',units);
                    var units_by_id = {};
                    for(var i = 0, len = units.length; i < len; i++){
                        units_by_id[units[i].id] = units[i];
                    }
                    self.set('units_by_id',units_by_id);
                    
                    return self.fetch('product.packaging', null, null);
                }).then(function(packagings){
                    self.set('product.packaging',packagings);
                    
                    return self.fetch('res.users', ['name','ean13'], [['ean13', '!=', false]]);
                }).then(function(users){
                    self.set('user_list',users);

                    return self.fetch('res.partner', ['name','ean13'], [['ean13', '!=', false]]);
                }).then(function(partners){
                    self.set('partner_list',partners);

                    return self.fetch('account.tax', ['amount', 'price_include', 'type']);
                }).then(function(taxes){
                    self.set('taxes', taxes);

                    return self.fetch(
                        'pos.session', 
                        ['id', 'journal_ids','name','user_id','config_id','start_at','stop_at'],
                        [['state', '=', 'opened'], ['user_id', '=', self.session.uid]]
                    );
                }).then(function(sessions){
                    self.set('pos_session', sessions[0]);

                    return self.fetch(
                        'pos.config',
                        ['name','journal_ids','shop_id','journal_id',
                         'iface_self_checkout', 'iface_led', 'iface_cashdrawer',
                         'iface_payment_terminal', 'iface_electronic_scale', 'iface_barscan', 'iface_vkeyboard',
                         'iface_print_via_proxy','iface_cashdrawer','state','sequence_id','session_ids'],
                        [['id','=', self.get('pos_session').config_id[0]]]
                    );
                }).then(function(configs){
                    var pos_config = configs[0];
                    self.set('pos_config', pos_config);
                    self.iface_electronic_scale    =  !!pos_config.iface_electronic_scale;  
                    self.iface_print_via_proxy     =  !!pos_config.iface_print_via_proxy;
                    self.iface_vkeyboard           =  !!pos_config.iface_vkeyboard; 
                    self.iface_self_checkout       =  !!pos_config.iface_self_checkout;
                    self.iface_cashdrawer          =  !!pos_config.iface_cashdrawer;

                    return self.fetch('sale.shop',[],[['id','=',pos_config.shop_id[0]]]);
                }).then(function(shops){
                    self.set('shop',shops[0]);

                    return self.fetch('product.pricelist',['currency_id'],[['id','=',self.get('shop').pricelist_id[0]]]);
                }).then(function(pricelists){
                    self.set('pricelist',pricelists[0]);

                    return self.fetch('res.currency',['symbol','position','rounding','accuracy','valor'],[['id','=',self.get('pricelist').currency_id[0]]]);
                }).then(function(currencies){
                    self.set('currency',currencies[0]);

                    return self.fetch('product.packaging',['ean','product_id']);
                }).then(function(packagings){
                    self.db.add_packagings(packagings);

                    return self.fetch('pos.category', ['id','name','parent_id','child_id','image'])
                }).then(function(categories){
                    self.db.add_categories(categories);

                    return self.fetch(
                        'product.product', 
                        ['name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 'variants',
                         'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description'],
                        [['sale_ok','=',true],['available_in_pos','=',true]],
                        {pricelist: self.get('shop').pricelist_id[0]} // context for price
                    );
                }).then(function(products){
                    self.db.add_products(products);

                    return self.fetch(
                            'account.bank.statement',
                            ['account_id','currency','journal_id','state','name','user_id','pos_session_id'],
                            [['state','=','open'],['pos_session_id', '=', self.get('pos_session').id]]
                        );
                    }).then(function(bank_statements){
                        var journals = new Array();
                        _.each(bank_statements,function(statement) {
                            journals.push(statement.journal_id[0])
                        });
                        self.set('bank_statements', bank_statements);
                        return self.fetch('account.journal', undefined, [['id','in', journals]]);
                    }).then(function(journals){
                        self.set('journals',journals);

                        // associate the bank statements with their journals. 
                        var bank_statements = self.get('bank_statements');
                        for(var i = 0, ilen = bank_statements.length; i < ilen; i++){
                            for(var j = 0, jlen = journals.length; j < jlen; j++){
                                if(bank_statements[i].journal_id[0] === journals[j].id){
                                    bank_statements[i].journal = journals[j];
                                    bank_statements[i].self_checkout_payment_method = journals[j].self_checkout_payment_method;
                                }
                            }
                        }
                        self.set({'cashRegisters' : new module.CashRegisterCollection(self.get('bank_statements'))});
                    });
            
            return loaded;
        },
        
	});
	
	
	
	module.Order = module.Order.extend({
		
		export_for_printing: function(){
            var orderlines = [];
            this.get('orderLines').each(function(orderline){
                orderlines.push(orderline.export_for_printing());
            });

            var paymentlines = [];
            this.get('paymentLines').each(function(paymentline){
                paymentlines.push(paymentline.export_for_printing());
            });
            var client  = this.get('client');
            var cashier = this.pos.get('cashier') || this.pos.get('user');
            var company = this.pos.get('company');
            var shop    = this.pos.get('shop');
            var date = new Date();

            return {
                orderlines: orderlines,
                paymentlines: paymentlines,
                subtotal: this.getSubtotal(),
                total_with_tax: this.getTotalTaxIncluded(),
                total_without_tax: this.getTotalTaxExcluded(),
                total_tax: this.getTax(),
                total_paid: this.getPaidTotal(),
                total_discount: this.getDiscountTotal(),
                change: this.getChange(),
                name : this.getName(),
                client: client ? client.name : null ,
                invoice_id: null,   //TODO
                cashier: cashier ? cashier.name : null,
                user_email: cashier ? cashier.email : null,
                date: { 
                    year: date.getFullYear(), 
                    month: date.getMonth(), 
                    date: date.getDate(),       // day of the month 
                    day: date.getDay(),         // day of the week 
                    hour: date.getHours(), 
                    minute: date.getMinutes() 
                }, 
                company:{
                    email: company.email,
                    website: company.website,
                    company_registry: company.company_registry,
                    contact_address: company.contact_address, 
                    vat: company.vat,
                    name: company.name,
                    phone: company.phone,
                    logo: company.logo,
                },
                shop:{
                    name: shop.name,
                },
                currency: this.pos.get('currency'),
            };
        },

	});
	
	module.ReceiptScreenWidget = module.ReceiptScreenWidget.extend({
		init: function(parent, options) {
        this._super(parent,options);
        this.logo = this.pos.get('company').logo
        this.valor = this.currency.valor
    	},
		
	});
	    
	
};