openerp.humanytek_pos = function (instance) {
	module = instance.point_of_sale;
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;
	
	var fetch = function(model, fields, domain, ctx){
        return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
    };
    
    module.PosWidget.include({
    	start: function() {
            var self = this;
            return self.pos.ready.done(function() {
                // remove default webclient handlers that induce click delay
                $(document).off();
                $(window).off();
                $('html').off();
                $('body').off();
                $(self.$el).parent().off();
                $('document').off();
                $('.oe_web_client').off();
                $('.openerp_webclient_container').off();


                self.renderElement();
                
                self.$('.neworder-button').click(function(){
                    self.pos.add_new_order();
                });

                self.$('.deleteorder-button').click(function(){
                    if( !self.pos.get('selectedOrder').is_empty() ){
                        self.screen_selector.show_popup('confirm',{
                            message: _t('Destroy Current Order ?'),
                            comment: _t('You will lose any data associated with the current order'),
                            confirm: function(){
                                self.pos.delete_current_order();
                            },
                        });
                    }else{
                        self.pos.delete_current_order();
                    }
                });
                
                //when a new order is created, add an order button widget
                self.pos.get('orders').bind('add', function(new_order){
                    var new_order_button = new module.OrderButtonWidget(null, {
                        order: new_order,
                        pos: self.pos
                    });
                    new_order_button.appendTo(this.$('.orders'));
                    new_order_button.selectOrder();
                }, self);

                self.pos.add_new_order();

                self.build_widgets();

                if(self.pos.config.iface_big_scrollbars){
                    self.$el.addClass('big-scrollbars');
                }

                self.screen_selector.set_default_screen();

                self.pos.barcode_reader.connect();

                instance.webclient.set_content_full_screen(true);

                self.$('.loader').animate({opacity:0},1500,'swing',function(){self.$('.loader').addClass('oe_hidden');});
                
                $('#custom_refund_button').click(function() {
                    self.pos.pos_widget.screen_selector.show_popup('authenticate',{
                        message: _t('Password'),
                        tex: _t(''),
                        confirm: function(){
                        },
                    });
                    $('.tex').val('').focus();
                });
        		$('#orders_all').css({'display':'none'});
        		$('#orders_all').change(function() {
        			$('#custom_refund_button').val("active")
        			var selected_order = $('#orders_all').val();
        			if (selected_order != 'Select order'){
    	    			$('#orders_all').css({'display':'none'});
    	    			$('#custom_refund_button').css({'display':'inline'});
    	            	var reference = $('#orders_all option:selected').attr('value');
    	            	$.when(new instance.web.Model("pos.order").get_func("search_read")([['pos_reference','=',reference]]).then(function(result){
    	    				if(result.length != 0){
	    						var id = result[0].id;
	    						if(id){
	    							self.pos.return_order_id = id
	    						}
	    						$.when(new instance.web.Model("pos.order.line").get_func("search_read")([['order_id','=',id]]).then(function(result){
	    							for(i=0;i<self.pos.attributes.pos_orders.length;i++){
	                        			self.pos.attributes.pos_orders[i].pos_order_lines = {};
	                        			if(self.pos.attributes.pos_orders[i].id == id){
	                        				var poLine = self.convert_poLine(result)
	                        				self.pos.attributes.pos_orders[i].pos_order_lines = poLine
	                        				return self.pos.add_new_pos_order(self.pos.attributes.pos_orders[i].pos_order_lines,self);
	                        			}
	                        		}
	    		            	})).then(function(){
	    		            	});
	    						return;
    	    				}
    	            	})).then(function(){
    	            	});
        			};
                });
                
                instance.web.cordova.send('posready');

                self.pos.push_order();

            }).fail(function(err){   // error when loading models data from the backend
                self.loading_error(err);
            });
        },
    	convert_poLine:function(record){
        	var converted_record = {};
        	for(j=0;j<record.length;j++){
        		converted_record[j] = {};
        		converted_record[j].description = false;
            	converted_record[j].description_sale = false;
            	converted_record[j].ean13 = false;
            	converted_record[j].id = record[j].product_id[0];
            	converted_record[j].name = record[j].product_id[1];
            	converted_record[j].options = {'quantity':record[j].qty,'quantityStr':(record[j].qty).toString(),'selected':true,'type': "unit"};
        	}
        	return converted_record; 
        },
    });
    
    module.PosModel.prototype.models.push({
        model: 'pos.order',
        fields: ['id','name','lines'],
        domain: null,
        loaded: function(self,orders){
        	self.orders = orders;
        	self.set('pos_orders',orders);
        },
    });
    
    module.PosModel = module.PosModel.extend({
    	add_new_pos_order: function(poLines,slf){
        	var pos_order = new module.Order({pos:slf.pos});
        	var new_products = {};
        	
        	for(i in poLines){
        		new_products[i] = slf.pos.db.get_product_by_id(poLines[i].id)
        		var attr = new_products[i]
                attr.pos = slf.pos;
                attr.order = pos_order;
        	}
            var new_poLines = {};
        	for(i in poLines){
        		var attr = new_products[i]
        		new_poLines[i] = new module.Orderline({}, {pos: slf.pos, order: pos_order, product: new_products[i]});
        			options = poLines[i].options || {};
        			var replacement = $('#custom_refund_button').val();
        			if (replacement == 'active'){
	        			new_poLines[i].quantity = options.quantity
	        			new_poLines[i].quantityStr = options.quantityStr
        			}
	                if(options.quantity !== undefined){
	                	new_poLines[i].set_quantity(options.quantity);
	                }
	                if(options.price !== undefined){
	                	new_poLines[i].set_unit_price(options.price);
	                }
	
	                var last_orderline = pos_order.getLastOrderline();
	                if( last_orderline && last_orderline.can_be_merged_with(new_poLines[i])){
	                    last_orderline.merge(new_poLines[i]);
	                }else{
	                	pos_order.get('orderLines').add(new_poLines[i]);
	                }
	                pos_order.selectLine(pos_order.getLastOrderline());
        		}
        	this.get('orders').add(pos_order);
            this.set('selectedOrder', pos_order);
        },
    });
    
    module.CustomValidatePopupWidget = module.PopUpWidget.extend({
        template: 'CustomValidatePopupWidget',
        show: function(options){
            var self = this;
            this._super();
            this.message = options.message || '';
            this.password_error = options.password_error || '';
            this.tex = options.tex || '';
            this.renderElement();
            this.$('.button.cancel').click(function(){
            	$('#custom_refund_button').val("inactive")
            	self.pos_widget.screen_selector.close_popup();
                if( options.cancel ){
                    options.cancel.call(self);
                }
            });
            this.$('.button.confirm').click(function(){
            	var entered_password = $('#password').val();
            	var db = self.pos.session.db
            	var username = self.pos.session.username
            	var env = {}
            	$('#custom_refund_button').css({'display':'none'});
            	new instance.web.Model("res.users").get_func("check_user")(db, username, entered_password, env).pipe(function(result){
            		if(result != false){
            			$('#orders_all').css({'display':'inline'});
            			var orders_all = ['<option value="">'+'Select order'+'</option>\n']
                        $.when(new instance.web.Model("pos.order").get_func("search_read")([]).then(function(result){
                    		if(result.length != 0){
                    			for(i=0;i<result.length;i++){
                    				if (result[i]['pos_reference'] && result[i]['return_order']!=true){
                    					orders_all.push('<option value="' + result[i]['pos_reference'] + '">' + result[i]['pos_reference'] + '</option>\n');
                    				}
                    			}
                    		}
                    		else{
                    			$('#custom_refund_button').val("inactive")
                    		}
                    		$('#orders_all').html(orders_all);
                    	}));
                    	self.pos_widget.screen_selector.close_popup();
            		}
            		else{
            			self.$(".password_error").html("Enter a valid password!");
            			self.$('.tex').val('').focus();
            		}
    			});
            });
        },
    });
    
    module.PosWidget.include({
    	build_widgets: function() {
            var self = this;

            // --------  Screens ---------

            this.product_screen = new module.ProductScreenWidget(this,{});
            this.product_screen.appendTo(this.$('.screens'));

            this.receipt_screen = new module.ReceiptScreenWidget(this, {});
            this.receipt_screen.appendTo(this.$('.screens'));

            this.payment_screen = new module.PaymentScreenWidget(this, {});
            this.payment_screen.appendTo(this.$('.screens'));

            this.clientlist_screen = new module.ClientListScreenWidget(this, {});
            this.clientlist_screen.appendTo(this.$('.screens'));

            this.scale_screen = new module.ScaleScreenWidget(this,{});
            this.scale_screen.appendTo(this.$('.screens'));


            // --------  Popups ---------

            this.error_popup = new module.ErrorPopupWidget(this, {});
            this.error_popup.appendTo(this.$el);

            this.error_barcode_popup = new module.ErrorBarcodePopupWidget(this, {});
            this.error_barcode_popup.appendTo(this.$el);

            this.error_traceback_popup = new module.ErrorTracebackPopupWidget(this,{});
            this.error_traceback_popup.appendTo(this.$el);

            this.confirm_popup = new module.ConfirmPopupWidget(this,{});
            this.confirm_popup.appendTo(this.$el);

            this.unsent_orders_popup = new module.UnsentOrdersPopupWidget(this,{});
            this.unsent_orders_popup.appendTo(this.$el);
            
            this.refund_popup = new module.CustomValidatePopupWidget(this,{});
            this.refund_popup.appendTo(this.$el);

            
            // --------  Misc ---------

            this.close_button = new module.HeaderButtonWidget(this,{
                label: _t('Close'),
                action: function(){ 
                    var self = this;
                    if (!this.confirmed) {
                        this.$el.addClass('confirm');
                        this.$el.text(_t('Confirm'));
                        this.confirmed = setTimeout(function(){
                            self.$el.removeClass('confirm');
                            self.$el.text(_t('Close'));
                            self.confirmed = false;
                        },2000);
                    } else {
                        clearTimeout(this.confirmed);
                        this.pos_widget.close();
                    }
                },
            });
            this.close_button.appendTo(this.$('.pos-rightheader'));

            this.notification = new module.SynchNotificationWidget(this,{});
            this.notification.appendTo(this.$('.pos-rightheader'));

            if(this.pos.config.use_proxy){
                this.proxy_status = new module.ProxyStatusWidget(this,{});
                this.proxy_status.appendTo(this.$('.pos-rightheader'));
            }

            this.username   = new module.UsernameWidget(this,{});
            this.username.replace(this.$('.placeholder-UsernameWidget'));

            this.action_bar = new module.ActionBarWidget(this);
            this.action_bar.replace(this.$(".placeholder-RightActionBar"));

            this.paypad = new module.PaypadWidget(this, {});
            this.paypad.replace(this.$('.placeholder-PaypadWidget'));

            this.numpad = new module.NumpadWidget(this);
            this.numpad.replace(this.$('.placeholder-NumpadWidget'));

            this.order_widget = new module.OrderWidget(this, {});
            this.order_widget.replace(this.$('.placeholder-OrderWidget'));

            this.onscreen_keyboard = new module.OnscreenKeyboardWidget(this, {
                'keyboard_model': 'simple'
            });
            this.onscreen_keyboard.replace(this.$('.placeholder-OnscreenKeyboardWidget'));

            // --------  Screen Selector ---------

            this.screen_selector = new module.ScreenSelector({
                pos: this.pos,
                screen_set:{
                    'products': this.product_screen,
                    'payment' : this.payment_screen,
                    'scale':    this.scale_screen,
                    'receipt' : this.receipt_screen,
                    'clientlist': this.clientlist_screen,
                },
                popup_set:{
                    'error': this.error_popup,
                    'error-barcode': this.error_barcode_popup,
                    'error-traceback': this.error_traceback_popup,
                    'confirm': this.confirm_popup,
                    'unsent-orders': this.unsent_orders_popup,
                    'authenticate': this.refund_popup,
                },
                default_screen: 'products',
                default_mode: 'cashier',
            });
            if(this.pos.debug){
                this.debug_widget = new module.DebugWidget(this);
                this.debug_widget.appendTo(this.$('.pos-content'));
            }
            this.disable_rubberbanding();
        },
    });
    
    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
    	init: function(parent, options) {
    		var self = this;
    		this._super(parent,options);
        },
        update_payment_summary: function() {
            var currentOrder = this.pos.get('selectedOrder');
            var paidTotal = currentOrder.getPaidTotal();
            var dueTotal = currentOrder.getTotalTaxIncluded();
            var remaining = dueTotal > paidTotal ? dueTotal - paidTotal : 0;
            var change = paidTotal > dueTotal ? paidTotal - dueTotal : 0;
            var replacement = $('#custom_refund_button').val();
            if (replacement == 'active'){
	            var selected_line =this.pos.get('selectedOrder').selected_paymentline;
	            if(selected_line){
	                selected_line.node.querySelector('input').value = -Math.abs(selected_line.amount);
	                selected_line.node.querySelector('input').readOnly = true;
	                this.$('.payment-due-total').html(this.format_currency(-Math.abs(dueTotal)));
	                this.$('.payment-paid-total').html(this.format_currency(-Math.abs(paidTotal)));
	                this.$('.payment-remaining').html(this.format_currency(remaining));
	                this.$('.payment-change').html(this.format_currency(change));
	            }
            }
            else{
            	this.$('.payment-due-total').html(this.format_currency(dueTotal));
                this.$('.payment-paid-total').html(this.format_currency(paidTotal));
                this.$('.payment-remaining').html(this.format_currency(remaining));
                this.$('.payment-change').html(this.format_currency(change));
            }

            if(currentOrder.selected_orderline === undefined){
                remaining = 1;  // What is this ? 
            }
                
            if(this.pos_widget.action_bar){
                this.pos_widget.action_bar.set_button_disabled('validation', !this.is_paid());
                this.pos_widget.action_bar.set_button_disabled('invoice', !this.is_paid());
            }
        },
    	validate_order: function(options) {
    		var self = this;
            var super1 = self._super;
        	module.Order.prototype.export_as_JSON = function() {
    			var replacement = $('#custom_refund_button').val();
    			var return_order_id = self.pos.return_order_id;
        		var orderLines, paymentLines;
                orderLines = [];
                (this.get('orderLines')).each(_.bind( function(item) {
                	
                	if (replacement == 'active'){
                		item['quantity'] = -Math.abs(item.quantity);
                		item['quantityStr'] = item['quantity'].toString();
                	}
                    return orderLines.push([0, 0, item.export_as_JSON()]);
                }, this));
                paymentLines = [];
                (this.get('paymentLines')).each(_.bind( function(item) {
                	if (replacement == 'active'){
                		item['amount'] = -Math.abs(item.amount);
                	}
                    return paymentLines.push([0, 0, item.export_as_JSON()]);
                }, this));
                return {
                    name: this.getName(),
                    amount_paid: this.getPaidTotal(),
                    amount_total: this.getTotalTaxIncluded(),
                    amount_tax: this.getTax(),
                    amount_return: this.getChange(),
                    lines: orderLines,
                    statement_ids: paymentLines,
                    pos_session_id: this.pos.pos_session.id,
                    partner_id: this.get_client() ? this.get_client().id : false,
                    user_id: this.pos.cashier ? this.pos.cashier.id : this.pos.user.id,
                    uid: this.uid,
                    sequence_number: this.sequence_number,
                    return_status : replacement,
                    return_order_id :return_order_id
                };
            }
        	super1.apply(self, arguments);
    	}
    });
    
    module.Order = module.Order.extend({
    	addPaymentline: function(cashregister) {
            var paymentLines = this.get('paymentLines');
            var newPaymentline = new module.Paymentline({},{cashregister:cashregister, pos:this.pos});
            var replacement = $('#custom_refund_button').val();
            newPaymentline.set_amount( Math.max(this.getDueLeft(),0) );
            paymentLines.add(newPaymentline);
            this.selectPaymentline(newPaymentline);
        },
        getChange: function() {
        	var replacement = $('#custom_refund_button').val();
        	if (replacement == 'active'){
        		return 0;
        	}
        	else{
        		return this.getPaidTotal() - this.getTotalTaxIncluded();
        	}
        },
        getName: function() {
            return this.get('name');
        },
    });
    
    module.PosModel.prototype.models.push({
        model:  'res.company',
        fields: [ 'currency_id', 'email', 'website', 'company_registry', 'vat',
                  'name', 'phone', 'partner_id' , 'country_id', 'tax_calculation_rounding_method',
                  'logo', 'street', 'street2', 'city', 'state_id', 'zip'],
        ids:    function(self){ return [self.user.company_id[0]] },
        loaded: function(self,companies){ self.company = companies[0]; },
    });
    
    module.ReceiptScreenWidget = module.ReceiptScreenWidget.extend({
    	finishOrder: function() {
    		this._super();
            $('#custom_refund_button').val("inactive")
        },
        
        getSelectedText: function(elementId) {
            var elt = document.getElementById(elementId);

            if (elt.selectedIndex == -1)
                return null;

            return elt.options[elt.selectedIndex].text;
        },

        refresh: function() {
        	var saleperson = this.getSelectedText('saleperson');
            var order = this.pos.get('selectedOrder');
        	var replacement = $('#custom_refund_button').val();
        	if (replacement == 'active'){
        		order.attributes.name = 'Refund'+' '+order.get('name');
        	}
        	else{
        		order.attributes.name = order.get('name');
        	}
        	$('.pos-receipt-container', this.$el).html(QWeb.render('PosTicket',{
                    widget:this,
                    order: order,
                    orderlines: order.get('orderLines').models,
                    paymentlines: order.get('paymentLines').models,
                    saleperson: saleperson
        	}));
        },
        
    });
};