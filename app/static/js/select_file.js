
		$(function () {
			$(window).resize(function () {
				var h = Math.max($(window).height() - 0, 420);
				$('#container, #data, #tree, #data .content').height(h).filter('.default').css('lineHeight', h + 'px');
			}).resize();

			$('#tree')
				.jstree({
					'core' : {
						'data' : {
							// 'url' : '?operation=get_node',
              				'url' : '/ajaxdata',
							'data' : function (node) {
								return { 'id' : node.id };
							}
						},
						'check_callback' : function(o, n, p, i, m) {
							if(m && m.dnd && m.pos !== 'i') { return false; }
							if(o === "move_node" || o === "copy_node") {
								if(this.get_node(n).parent === this.get_node(p).id) { return false; }
							}
							return true;
						},
						'themes' : {
							'responsive' : false,
							'variant' : 'small',
							'stripes' : true
						}
					},
					'sort' : function(a, b) {
						return this.get_type(a) === this.get_type(b) ? (this.get_text(a) > this.get_text(b) ? 1 : -1) : (this.get_type(a) >= this.get_type(b) ? 1 : -1);
					},
					'contextmenu' : {
						'items' : function(node) {
							var tmp = $.jstree.defaults.contextmenu.items();
							delete tmp.create.action;
							tmp.create.label = "New";
							tmp.create.submenu = {
								"create_folder" : {
									"separator_after"	: true,
									"label"				: "Folder",
									"action"			: function (data) {
										var inst = $.jstree.reference(data.reference),
											obj = inst.get_node(data.reference);
										inst.create_node(obj, { type : "default" }, "last", function (new_node) {
											setTimeout(function () { inst.edit(new_node); },0);
										});
									}
								},
								"create_file" : {
									"label"				: "File",
									"action"			: function (data) {
										var inst = $.jstree.reference(data.reference),
											obj = inst.get_node(data.reference);
										inst.create_node(obj, { type : "file" }, "last", function (new_node) {
											setTimeout(function () { inst.edit(new_node); },0);
										});
									}
								}
							};
							if(this.get_type(node) === "file") {
								delete tmp.create;
							}
							return tmp;
						}
					},
					'types' : {
						'default' : { 'icon' : 'folder' },
						'file' : { 'valid_children' : [], 'icon' : 'file' }
					},
					'unique' : {
						'duplicate' : function (name, counter) {
							return name + ' ' + counter;
						}
					},
					'plugins' : ['state','dnd','sort','types','contextmenu','unique']
				})
				.on('delete_node.jstree', function (e, data) {
					$.get('?operation=delete_node', { 'id' : data.node.id })
						.fail(function () {
							data.instance.refresh();
						});
				})
				.on('create_node.jstree', function (e, data) {
					$.get('?operation=create_node', { 'type' : data.node.type, 'id' : data.node.parent, 'text' : data.node.text })
						.done(function (d) {
							data.instance.set_id(data.node, d.id);
						})
						.fail(function () {
							data.instance.refresh();
						});
				})
				.on('rename_node.jstree', function (e, data) {
					$.get('?operation=rename_node', { 'id' : data.node.id, 'text' : data.text })
						.done(function (d) {
							data.instance.set_id(data.node, d.id);
						})
						.fail(function () {
							data.instance.refresh();
						});
				})
				.on('move_node.jstree', function (e, data) {
					$.get('?operation=move_node', { 'id' : data.node.id, 'parent' : data.parent })
						.done(function (d) {
							//data.instance.load_node(data.parent);
							data.instance.refresh();
						})
						.fail(function () {
							data.instance.refresh();
						});
				})
				.on('copy_node.jstree', function (e, data) {
					$.get('?operation=copy_node', { 'id' : data.original.id, 'parent' : data.parent })
						.done(function (d) {
							//data.instance.load_node(data.parent);
							data.instance.refresh();
						})
						.fail(function () {
							data.instance.refresh();
						});
				})
				.on('changed.jstree', function (e, data) {
					if(data && data.selected && data.selected.length) {
						$.get('/ajaxdata?operation=get_content&id=' + data.selected.join(':'), function (d) {
							console.log(d)
							show_catalog('content',d)
							if(d && typeof d.type !== 'undefined') {
					
								
								// $('#data .content').hide();
								// alert(d.icon)
								// switch(d.type) {
								// 	case 'text':
								// 	case 'txt':
								// 	case 'md':
								// 	case 'htaccess':
								// 	case 'log':
								// 	case 'sql':
								// 	case 'php':
								// 	case 'js':
								// 	case 'json':
								// 	case 'css':
								// 	case 'html':
								// 		$('#data .code').show();
								// 		$('#code').val(d.content);
								// 		break;
								// 	case 'png':
								// 	case 'jpg':
								// 	case 'jpeg':
								// 	case 'bmp':
								// 	case 'gif':
								// 		$('#data .image img').one('load', function () { $(this).css({'marginTop':'-' + $(this).height()/2 + 'px','marginLeft':'-' + $(this).width()/2 + 'px'}); }).attr('src',d.content);
								// 		$('#data .image').show();
								// 		break;
								// 	default:
								// 		$('#data .default').html(d.content).show();
								// 		break;
								// }
							}
						});
					}
					else {
						// $('#data .content').hide();
						// $('#data .default').html('Select a file from the tree.').show();
					}
				});
		});

		function show_catalog(id,jsondata){
			// var childs = jsondata[0].children
			var litag = '<ul>'
			var text = '';
			$.each(jsondata,function(i,childs){
				// console.log(childs.id)
				text = childs.id;
				let arr = childs.children.sort(compare('children'));
				$.each(arr,function(i,val){
					// console.log(val)
					if(val && typeof val.type !== 'undefined') {
						litag += '<li onclick="selectfile(this)" data-id="'+val.id+'" title="'+val.text+'"><i class="fa fa-file"></i><p>'+ val['text'] + '</p></li>'
					}
					else{
						litag += '<li onclick="get_catelog(this)" data-id="'+val.id+'" title="'+val.text+'"><i class="fa fa-folder"></i><p>'+ val['text'] + '</p></li>'
					}
				});
			});

			litag += '</ul>'
			// console.log(litag)
			
			$('#'+id).html(litag)
			console.log(text)
			let textlist = text.split('\\')
			console.log(textlist.length)
			var headernav = '<a onclick="get_catelog(this)" data-id="%23" href="javascript:;">?????????<i class="fa fa-chevron-right"></i></a>'
			$.each(textlist,function(i,val){
				if(val != ''){
					var tlength = text.indexOf(val) + val.length
					var data_id = text.substring(0,tlength)
					if (data_id.indexOf('\\') == -1){
						data_id = data_id + '\\'
					}
					headernav += '<a onclick="get_catelog(this)" href="javascript:;" data-id="'+ data_id +'">'+val+'<i class="fa fa-chevron-right"></i></a>'
				}
			});
			// console.log(headernav)
			$('.dizhi').html(headernav)

			$('#back').attr('data-id',text.substring(0,text.lastIndexOf('\\')))
			// $('#fname').text()



		}

		function get_catelog(id){
			var id_data = $(id).attr('data-id');
			$.get('/ajaxdata?operation=get_content&id='+id_data,function(d){
				show_catalog('content',d);
			});
		}
		  //?????????????????????
		function compare(property) {
      		return (firstobj, secondobj) => {
				const firstValue = firstobj[property];
				const secondValue = secondobj[property];
        		return secondValue - firstValue; //??????
      		};
    	}

		function selectfile(id){
			var namepath = $(id).attr('data-id');
			$('#fname').text(decodeURIComponent(namepath));
		}