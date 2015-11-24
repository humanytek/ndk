openerp.hmtk_ndk_product_customization = function(instance) {
	var _t = instance.web._t, 
		_lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	instance.web.hmtk_ndk_product_customization = instance.web.hmtk_ndk_product_customization || {};
	//instance.web.views.add('tree_jzebra_quick_print', 'instance.web.hmtk_product_customization.QuickPrintListView');
	instance.web.views.add('tree_jzebra_quick_edit', 'instance.web.hmtk_ndk_product_customization.QuickEditListView');
	instance.web.hmtk_ndk_product_customization.QuickEditListView = instance.web.ListView.extend({
		init: function() {
            this._super.apply(this, arguments);
		},
		
		qzReady: function() {
        	var qz = document.getElementById('qz');
        	if (qz != null){
        		qz.findPrinter();
			window['qzLoaded'] = true;
        	}
        },        
        qzDoneAppending: function(){
        	var qz = document.getElementById('qz');
        	if (qz != null){
        		qz.print();
        	}
        },
        
        qzDonePrinting: function(){
//        	$(".oe_searchview_clear").trigger('click');
		},
        
		monitorPrinting: function() {
			var qz = document.getElementById('qz');
            if (qz != null) {
               if (!qz.isDonePrinting()) {
                  window.setTimeout('monitorPrinting()', 100);
               } else {
                  var e = qz.getException();
                  if (e != null){
                  	alert("Exception occured: " + e.getLocalizedMessage());
                  }
               }
            } else {
               alert("Applet not loaded!");
            }
        },
		
		start:function(){
			window['qzDoneAppending'] = this.qzDoneAppending;
			window['monitorPrinting'] = this.monitorPrinting;
			window['qzDonePrinting'] = this.qzDonePrinting;
			var qz = document.getElementById('qz');
			if (qz){
				console.log('Remove qz');
				qz.parentNode.removeChild(qz);
			}
			
			this.$el.parent().prepend(QWeb.render("jzebra-applet", {widget: this}));
			window['qzLoaded'] = false;
			window['qzReady'] = this.qzReady;
            var tmp = this._super.apply(this, arguments);
            var self = this;
            var defs = [];
            var mod = new instance.web.Model(this.model, this.dataset.context, this.dataset.domain);
            //package_label
            this.$el.parent().find('#qz_zpl_print').click(function(){
            	var sel_ids = self.get_selected_ids();
		console.log("sel_ids", sel_ids)
            	if (sel_ids.length === 0){
            		if (self.dataset.ids.length === 1){
            			sel_ids = self.dataset.ids;
            		}
            	}
            	if (sel_ids.length > 0){
            		var zpl_package_template = '';
            		var zpl_exhibitor_template = '';
            		mod.call("get_zpl_command", [sel_ids]).done(function(result){
                		if (result){
                			var qz = document.getElementById('qz');
                			if (qz != null) {
                				//zpl_visitor_template = result['visitor'];
                				zpl_package_template = result['package'];
                				new instance.web.Model("ir.config_parameter").call('get_param', ['web.base.url']).pipe(function(web_base_url){
						window['qz_base_url'] = web_base_url;
        	        			}).done(function(){
							//qz.setEncoding("cp1252");
        	        				var res = result['result'];
        	            			for(var i=0, len=res.length; i<len; i++){
        	            				if (res[i]){
    	            						/*if (res[i][0] === 'visitor'){
    	            							qz.append(zpl_visitor_template);
    	            						}*/
    	            						if (res[i][0] === 'package'){
									console.log(res[i][0], zpl_package_template);
    	            							qz.append(zpl_package_template);
    	            						}
    	            						//qz.appendFile(window['qz_base_url'] + '/' + res[i][1]);
								console.log(res[i][1]);								
								qz.append(res[i][1]);
    	            						qz.print();
    	            					}	
        	            			}
        	        			});
                            }
                            else{
                            	alert('Applet not loaded');
                            }
                            monitorPrinting();	
                    	}	
                	});	
            	}
            	else {
            		alert('Please select at-least one record');
            	}
            	
            });
            
          //product_label
            this.$el.parent().find('#qz_zpl_print_product_label').click(function(){
            	var sel_ids = self.get_selected_ids();
		console.log("sel_ids", sel_ids)
            	if (sel_ids.length === 0){
            		if (self.dataset.ids.length === 1){
            			sel_ids = self.dataset.ids;
            		}
            	}
            	if (sel_ids.length > 0){
            		var zpl_product_label_template = '';
            		mod.call("get_zpl_product_command", [sel_ids]).done(function(result){
                		if (result){
                			var qz = document.getElementById('qz');
                			if (qz != null) {
                				zpl_product_label_template = result['product_label'];
                				new instance.web.Model("ir.config_parameter").call('get_param', ['web.base.url']).pipe(function(web_base_url){
						window['qz_base_url'] = web_base_url;
        	        			}).done(function(){
        	        				var res = result['result'];
        	            			for(var i=0, len=res.length; i<len; i++){
        	            				if (res[i]){
    	            						if (res[i][0] === 'product_label'){
									console.log(res[i][0], zpl_product_label_template);
    	            							qz.append(zpl_product_label_template);
    	            						}
								console.log(res[i][1]);								
								qz.append(res[i][1]);
    	            						qz.print();
    	            					}	
        	            			}
        	        			});
                            }
                            else{
                            	alert('Applet not loaded');
                            }
                            monitorPrinting();	
                    	}	
                	});	
            	}
            	else {
            		alert('Please select at-least one record');
            	}
            	
            });
            
            //barcode_label
            this.$el.parent().find('#qz_zpl_print_product').click(function(){
            	var sel_ids = self.get_selected_ids();
		console.log("sel_ids", sel_ids)
            	if (sel_ids.length === 0){
            		if (self.dataset.ids.length === 1){
            			sel_ids = self.dataset.ids;
            		}
            	}
            	if (sel_ids.length > 0){
            		var zpl_barcode_template = '';
            		mod.call("get_zpl_barcode", [sel_ids]).done(function(result){
                		if (result){
                			var qz = document.getElementById('qz');
                			if (qz != null) {
                				//zpl_visitor_template = result['visitor'];
                				zpl_barcode_template = result['barcode'];
                				console.log('barcode', zpl_barcode_template);
                				new instance.web.Model("ir.config_parameter").call('get_param', ['web.base.url']).pipe(function(web_base_url){
						window['qz_base_url'] = web_base_url;
        	        			}).done(function(){
							//qz.setEncoding("cp1252");
        	        				var res = result['result'];
        	            			for(var i=0, len=res.length; i<len; i++){
        	            				if (res[i]){
    	            						/*if (res[i][0] === 'visitor'){
    	            							qz.append(zpl_visitor_template);
    	            						}*/
    	            						if (res[i][0] === 'barcode'){
									console.log(res[i][0], zpl_barcode_template);
    	            							qz.append(zpl_barcode_template);
    	            						}
    	            						//qz.appendFile(window['qz_base_url'] + '/' + res[i][1]);
								console.log(res[i][1]);								
								qz.append(res[i][1]);
    	            						qz.print();
    	            					}	
        	            			}
        	        			});
                            }
                            else{
                            	alert('Applet not loaded');
                            }
                            monitorPrinting();	
                    	}	
                	});	
            	}
            	else {
            		alert('Please select at-least one record');
            	}
            	
            });
            
            
	        return $.when(tmp, defs);
		},
	});
 
};
	
