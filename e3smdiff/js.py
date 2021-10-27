resizable = """
const Resizable = {};
Resizable.activeContentWindows = [];
Resizable.activeResizers = [];
Resizable.currentResizer = null;

Resizable.Sides = {
  TOP: "TOP",
  BOTTOM: "BOTTOM",
  LEFT: "LEFT",
  RIGHT: "RIGHT"
};

Resizable.Classes = {
  WINDOW_TOP: "resizable-top",
  WINDOW_BOTTOM: "resizable-bottom",
  WINDOW_LEFT: "resizable-left",
  WINDOW_RIGHT: "resizable-right"
};


Resizable.initialise = function(parentId, initialSizes, resizerThickness){
  //Find left window
  Resizable.resizerThickness = resizerThickness ? resizerThickness : 4;
  Resizable.initialSizes = initialSizes;
  var parent = document.getElementById(parentId);
  var parentWindow = new Resizable.ContentWindow(null, parseInt(parent.style.width, 10), parseInt(parent.style.height, 10), parent);
  Resizable.activeContentWindows.push(parentWindow);
  Resizable.setupChildren(parentWindow);
};

Resizable.setupChildren = function(parentWindow){
  var childInfo = parentWindow.findChildWindowElements();
  if(childInfo.child1 == null){
    //No children found
    return;
  }
  var sizeFraction;
  sizeFraction = Resizable.initialSizes[childInfo.child1.id];
  if(sizeFraction == undefined)
    sizeFraction = 0.5;
  if(childInfo.isHorizontal){
    parentWindow.splitHorizontally(sizeFraction, childInfo.child1, childInfo.child2);
  }else{
    parentWindow.splitVertically(sizeFraction, childInfo.child1, childInfo.child2);
  }
  //Set up the children of the newly created windows
  var childWindow1 = Resizable.activeContentWindows[Resizable.activeContentWindows.length-2];
  var childWindow2 = Resizable.activeContentWindows[Resizable.activeContentWindows.length-1];
  Resizable.setupChildren(childWindow1);
  Resizable.setupChildren(childWindow2);

};

Resizable.ContentWindow = class{
  
  constructor(parent, width, height, div){
    this.parent = parent;
    this.width = width;
    this.height = height;
    this.sizeFractionOfParent = 0.5;

    if(div == null){
      this.divId = "contentWindow" + Resizable.activeContentWindows.length;

      var div = document.createElement('div');
      div.id = this.divId;
      div.classList.add('contentWindow');

      //Insert the div with correct ID into the parent window; or body if parent is null
      if(parent != null){
        parent.getDiv().appendChild(div);
      }else{
        document.body.insertAdjacentHTML('afterbegin', htmlToAdd);
      }
    }
    else{
      if(div.id == "")
        div.id = "contentWindow" + Resizable.activeContentWindows.length;
      this.divId = div.id;
      this.getDiv().classList.add("contentWindow");
    }

    this.children = [];
    this.isSplitHorizontally = false;
    this.isSplitVertically = false;
    this.childResizer = null;
    this.minWidth = 20;
    this.minHeight = 20;
    this.originalMinSize = 20;
    this.childResizerThickness = Resizable.resizerThickness;


    this.getDiv().style.position = "absolute";
    //this.getDiv().style.overflow = "hidden"; -YSK
    this.getDiv().style.whiteSpace = "nowrap"; // +YSK
    this.getDiv().style.overflow = "auto"; // +YSK

    this.getDiv().style.width = Math.round(this.width)+"px";
    this.getDiv().style.height = Math.round(this.height)+"px";

    Resizable.activeContentWindows.push(this);
    this.calculateSizeFractionOfParent();

  }

  getDiv(){
    return document.getElementById(this.divId);
  }

  getDivId(){
    return this.divId;
  }

  findChildWindowElements(){
    //Cannot have more than two direct children
    var child1, child2, isHorizontal = false;
    //Find left child
    if(document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_LEFT}`).length > 0){
      child1 = document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_LEFT}`)[0];
      if(document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_LEFT}`).length > 0){
        child2 = document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_RIGHT}`)[0];
      }else{
        console.error(`${this.divId} has left child but not right`);
      }
      isHorizontal = true;
    }
    if(document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_TOP}`).length > 0){
      if(child1 != undefined){
        console.error(`${this.divId} has both left and top children`);
        return;
      }else{
        child1 = document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_TOP}`)[0];
        if(document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_BOTTOM}`).length > 0){
          child2 = document.querySelectorAll(`#${this.divId} > .${Resizable.Classes.WINDOW_BOTTOM}`)[0];
        }else{
          console.error(`${this.divId} has top child but not bottom`);
        }
      }
      isHorizontal = false;
    }

    return {child1: child1, child2: child2, isHorizontal: isHorizontal};

  }

  resize(side, mousePos){

    if(this.parent == null){
      return;
    }

    switch(side){
      case Resizable.Sides.TOP:
        //Based on position of resizer line
        this.changeSize(this.parent.width, parseInt(this.parent.getDiv().style.height) - mousePos);
        this.getDiv().style.top = Math.round(mousePos) +"px";
        break;
      case Resizable.Sides.BOTTOM:
        this.changeSize(this.parent.width, mousePos - this.getDiv().getBoundingClientRect().top);
        break;
      case Resizable.Sides.LEFT:   
        //Based on position of resizer line
        this.changeSize(parseInt(this.parent.getDiv().style.width) - mousePos, this.parent.height);
        this.getDiv().style.left = Math.round(mousePos) +"px";
        break;
      case Resizable.Sides.RIGHT:
        this.changeSize(mousePos - this.getDiv().getBoundingClientRect().left, this.parent.height);
        break;
      default:
        console.error("Window.resize: incorrect side");

    }

    if(this.children.length > 0){
      this.childrenResize();
    }

    if(this.parent != null){
      this.calculateSizeFractionOfParent();
      this.getSibling().calculateSizeFractionOfParent();
      siblingWindowErrorCorrect(this);
    }

    this.repositionChildResizer();
    
    Resizable.windowResized();

  }

  calculateSizeFractionOfParent(){
    if(this.parent == null){
      this.sizeFractionOfParent = 1.0;
    }else{
      if(this.parent.isSplitHorizontally){
        this.sizeFractionOfParent = this.width / this.parent.width;

      }else if (this.parent.isSplitVertically){
        this.sizeFractionOfParent = this.height / this.parent.height;
      }
    }

  }

  getSibling(){
    if(this.parent == null)
      return null;
    if(this.parent.children[0] == this)
      return this.parent.children[1];
    else return this.parent.children[0];
  }

  childrenResize(){
    if(this.children.length == 0)
      return; //Content window has no children

    if(this.isSplitHorizontally){
      var height = this.height;
      this.children[0].changeSize(this.width * this.children[0].sizeFractionOfParent, height);
      this.children[1].changeSize(this.width * this.children[1].sizeFractionOfParent, height);
      this.children[1].getDiv().style.left = parseInt(this.children[0].getDiv().style.width) + this.childResizer.lineThickness + "px";
    }else if(this.isSplitVertically){
      this.children[0].changeSize(this.width,  this.height * this.children[0].sizeFractionOfParent);
      this.children[1].changeSize(this.width, this.height * this.children[1].sizeFractionOfParent);
      this.children[1].getDiv().style.top = parseInt(this.children[0].getDiv().style.height) + this.childResizer.lineThickness + "px";
    }

    this.children[0].childrenResize();
    this.children[1].childrenResize();

    this.repositionChildResizer();

  }

  toString(){
    return `divId = ${this.divId}, parent = ${this.parent.getDivId()}, width = ${this.width}, height = ${this.height}`;
  }

  changeSize(width, height){
    
    if(width < this.minWidth){
      width = this.minWidth;
    }
    if(height < this.minHeight)
      height = this.minHeight;


    if(this.parent != null){
      if(width > this.parent.width - this.getSibling().minWidth && this.parent.isSplitHorizontally){
        width = this.parent.width - this.getSibling().minWidth;
        this.parent.repositionChildResizer();
      }
      if(height > this.parent.height - this.getSibling().minHeight && this.parent.isSplitVertically){
        height = this.parent.height - this.getSibling().minHeight;
        this.parent.repositionChildResizer();
      }
    }

    if(this.parent == null){
      if(width > window.innerWidth)
        width = window.innerWidth;
      if(height > window.height)
        height = window.innerHeight;
    }else{
      if(width > this.parent.width){
        width = this.parent.width;
      }
      if(height > this.parent.height){
        height = this.parent.height;
      }
    }

    width = Math.round(width);
    height = Math.round(height);
    this.getDiv().style.width = width + "px";
    this.getDiv().style.height = height + "px";
    this.width = width;
    this.height = height;

  }

  repositionChildResizer(){
    if(this.childResizer != null)
      this.childResizer.reposition();
  }

  calculateMinWidthHeight(){

    if(this.children.length > 0){
      //Recursively call this on all descendants
      this.children[0].calculateMinWidthHeight();
      this.children[1].calculateMinWidthHeight();
      if(this.isSplitHorizontally){
        this.minWidth = this.children[0].minWidth + this.children[1].minWidth;
        if(this.children[0].minHeight > this.children[1].minHeight)
          this.minHeight = this.children[0].minHeight;
        else
          this.minHeight = this.children[1].minHeight;
      }else if(this.isSplitVertically){
        this.minHeight = this.children[0].minHeight + this.children[1].minHeight;
        if(this.children[0].minWidth > this.children[1].minWidth)
          this.minWidth = this.children[0].minWidth;
        else
          this.minWidth = this.children[1].minWidth;
      }
    }else{
      this.minWidth = this.originalMinSize;
      this.minHeight = this.originalMinSize;

    }

    this.minWidth = Math.round(this.minWidth);
    this.minHeight = Math.round(this.minHeight);

  }

  getTopLevelParent(){
    var parentToReturn = this;
    while(parentToReturn.parent != null){
      parentToReturn = parentToReturn.parent;
    }
    return parentToReturn;
  }

  splitHorizontally(leftWindowSizeFraction, leftDiv, rightDiv){

    this.isSplitHorizontally = true;

    var leftWidth = (this.width * leftWindowSizeFraction) - this.childResizerThickness/2;

    if(leftWidth != null && leftDiv != null){
      this.getDiv().appendChild(leftDiv);
    }
    if(rightDiv != null){
      this.getDiv().appendChild(rightDiv);
    }

    var w1 = new Resizable.ContentWindow(this, leftWidth, this.height, leftDiv);
    var w2 = new Resizable.ContentWindow(this, this.width - leftWidth - this.childResizerThickness/2, this.height, rightDiv);
    w2.getDiv().style.left = Math.round(leftWidth + this.childResizerThickness/2) + "px";

    this.childResizer = new Resizable.Resizer(this, w1, w2, true);
    this.childResizer.getDiv().style.left = Math.round(leftWidth - this.childResizerThickness/2) + "px";

    this.children.push(w1);
    this.children.push(w2);

    this.getTopLevelParent().calculateMinWidthHeight();

  }

  splitVertically(topWindowSizeFraction, topDiv, bottomDiv){

    this.isSplitVertically = true;

    var topHeight = (this.height * topWindowSizeFraction) - this.childResizerThickness/2;
    
    if(topDiv != null)
      this.getDiv().appendChild(topDiv);
    if(bottomDiv != null)
      this.getDiv().appendChild(bottomDiv);

    var w1 = new Resizable.ContentWindow(this, this.width, topHeight - this.childResizerThickness/2, topDiv);
    var w2 = new Resizable.ContentWindow(this, this.width, this.height - topHeight - this.childResizerThickness/2, bottomDiv);
    w2.getDiv().style.top = Math.round(topHeight + this.childResizerThickness/2)  + "px";

    this.childResizer = new Resizable.Resizer(this, w1, w2, false);
    this.childResizer.getDiv().style.top = Math.round(topHeight - this.childResizerThickness/2) + "px";

    this.children.push(w1);
    this.children.push(w2);

    this.getTopLevelParent().calculateMinWidthHeight();

  }

};

Resizable.parentResize = function(width, height){
  const parentWindow = Resizable.activeContentWindows[0];
  parentWindow.changeSize(width, height);
  parentWindow.repositionChildResizer();
  if (parentWindow.children.length > 0) {
    parentWindow.childrenResize();
  }

  if (parentWindow.parent != null) {
    parentWindow.calculateSizeFractionOfParent();
    parentWindow.getSibling().calculateSizeFractionOfParent();
    siblingWindowErrorCorrect(parentWindow);
  }

  parentWindow.repositionChildResizer();
  Resizable.windowResized();
}

function resizerMouseDown(e) {
  e.preventDefault();
  Resizable.resizingStarted();
  e.stopPropagation();
  Resizable.currentResizer = getResizerFromDiv(this.id);
  window.addEventListener('mousemove', Resizable.currentResizer.resize);
  window.addEventListener('mouseup', Resizable.currentResizer.cancelResize);
}

function resizerTouchStart(e) {
  Resizable.resizingStarted();
  Resizable.currentResizer = getResizerFromDiv(this.id);
  window.addEventListener('touchmove', Resizable.currentResizer.resize);
  window.addEventListener('touchend', Resizable.currentResizer.cancelResize);
}

function attachResizerEvents(){
  var elements = document.querySelectorAll('.resizer');
  if (elements) {
    elements.forEach(function(el){
      el.addEventListener('mousedown', resizerMouseDown);
      el.addEventListener('touchstart', resizerTouchStart);
    });
  }
}

function clearResizerEvents() {
  var elements = document.querySelectorAll('.resizer');
  if (elements) {
    elements.forEach(function(el){
      el.removeEventListener('mousedown', resizerMouseDown);
      el.removeEventListener('touchstart', resizerTouchStart);
    });
  }
}

function getResizerFromDiv(divId){
  for(var i = 0; i < Resizable.activeResizers.length; i++){
    if(Resizable.activeResizers[i].getDivId() == divId){
      return Resizable.activeResizers[i];
    }
  }
  console.error("getResizerFromDiv failed to find resizer");
  return null;
}

function siblingWindowErrorCorrect(child){
  child.getSibling().sizeFractionOfParent = 1 - child.sizeFractionOfParent;
}


Resizable.windowResized = function(){
  //Code to run when any window is resized should be placed here.
};

Resizable.resizingEnded = function() {
  //Runs whenever a resizer is clicked
}

Resizable.resizingStarted = function() {
  //Runs on the next 'mouseup' or 'touchend' events after a resizer is clicked
}
















Resizable.Resizer = class{
  constructor(parent, window1, window2, isHorizontal){
    this.parent = parent;
    this.isHorizontal = isHorizontal;
    if(this.isHorizontal){
      this.leftWindow = window1;
      this.rightWindow = window2;
    }else{
      //Vertical Resizer
      this.topWindow = window1;
      this.bottomWindow = window2;
    }

    this.divId = `resizer${Resizable.activeResizers.length}`;

    var div = document.createElement('div');
    div.id = this.divId;
    div.classList.add('resizer');
    parent.getDiv().appendChild(div);

    if(this.isHorizontal){
      this.getDiv().classList.add("horizontalResizer");
      this.getDiv().style.cursor ="ew-resize";
    }else{
      this.getDiv().classList.add("verticalResizer");
      this.getDiv().style.cursor = "ns-resize";
    }

    this.getDiv().style.position = "absolute";

    //this.lineThickness = 4;
    this.lineThickness = Resizable.resizerThickness;
    if(isHorizontal){
      this.getDiv().style.width = Math.round(this.lineThickness) + "px";
      this.getDiv().style.height = this.parent.height + "px";
    }else{
      this.getDiv().style.width = this.parent.width + "px";
      this.getDiv().style.height = this.lineThickness + "px";
    }

    this.reposition();


    Resizable.activeResizers.push(this);
    clearResizerEvents();
    attachResizerEvents();

  }

  getDiv(){
    return document.getElementById(this.divId);
  }

  getDivId(){
    return this.divId;
  }

  reposition(){

    if(this.isHorizontal){
      this.getDiv().style.left = this.leftWindow.getDiv().style.width;
      this.getDiv().style.height = this.parent.getDiv().style.height;
    }else{
      this.getDiv().style.top = this.topWindow.getDiv().style.height;
      this.getDiv().style.width = this.parent.getDiv().style.width;
    }

  }


  resize(e){
    

    var inputX = e.pageX;
    var inputY = e.pageY;
    if(inputX == undefined){
      inputX = e.changedTouches[0].pageX;
    }
    if(inputY == undefined){
      inputY = e.changedTouches[0].pageY;
    }else{
      e.preventDefault();
    }

    //Find the current resizer being clicked
    if(Resizable.currentResizer == null){
      for(var i = 0; i < Resizable.activeResizers.length; i++){
        if(Resizable.activeResizers[i].getDiv() == e.target){
          Resizable.currentResizer = Resizable.activeResizers[i];
        }
      }
    }

    if(Resizable.currentResizer.isHorizontal){
      //Change size of left window
      Resizable.currentResizer.leftWindow.resize(Resizable.Sides.RIGHT, inputX);
      //Change the size of the right window
      Resizable.currentResizer.getDiv().style.left = Resizable.currentResizer.leftWindow.getDiv().style.width;
      Resizable.currentResizer.rightWindow.resize(Resizable.Sides.LEFT, parseInt(Resizable.currentResizer.getDiv().style.left));
    }else{
      //Change size of the top window
      Resizable.currentResizer.topWindow.resize(Resizable.Sides.BOTTOM, inputY);
      //Change size of the bottom window and move resizer
      Resizable.currentResizer.getDiv().style.top = Resizable.currentResizer.topWindow.getDiv().style.height;
      Resizable.currentResizer.bottomWindow.resize(Resizable.Sides.TOP, parseInt(Resizable.currentResizer.getDiv().style.top));
    }

  }

  delete(){
    for(var i = 0; i < Resizable.activeResizers.length; i++){
      if(Resizable.activeResizers[i] == this)
        Resizable.activeResizers.splice(i,1);
    }
    this.getDiv().parentNode.removeChild(this.getDiv());
  }

  cancelResize(e){
    window.removeEventListener("mousemove", Resizable.currentResizer.resize);
    window.removeEventListener("mouseup", Resizable.currentResizer.cancelResize);

    window.removeEventListener("touchmove", Resizable.currentResizer.resize);
    window.removeEventListener("touchend", Resizable.currentResizer.cancelResize);
    Resizable.currentResizer = null;
    Resizable.resizingEnded();
  }

};
"""

tree = """
/**
* TreeJS is a JavaScript librarie for displaying TreeViews
* on the web.
*
* @author Matthias Thalmann
* @repository https://github.com/m-thalmann/treejs
*/

function TreeView(root, container, options){
	var self = this;

	/*
	* Konstruktor
	*/
	if(typeof root === "undefined"){
		throw new Error("Parameter 1 must be set (root)");
	}

	if(!(root instanceof TreeNode)){
		throw new Error("Parameter 1 must be of type TreeNode");
	}

	if(container){
		if(!TreeUtil.isDOM(container)){
			container = document.querySelector(container);

			if(container instanceof Array){
				container = container[0];
			}

			if(!TreeUtil.isDOM(container)){
				throw new Error("Parameter 2 must be either DOM-Object or CSS-QuerySelector (#, .)");
			}
		}
	}else{
		container = null;
	}

	if(!options || typeof options !== "object"){
		options = {};
	}

	/*
	* Methods
	*/
	this.setRoot = function(_root){
		if(root instanceof TreeNode){
			root = _root;
		}
	}

	this.getRoot = function(){
		return root;
	}

	this.expandAllNodes = function(){
		root.setExpanded(true);

		root.getChildren().forEach(function(child){
			TreeUtil.expandNode(child);
		});
	}

	this.expandPath = function(path){
		if(!(path instanceof TreePath)){
			throw new Error("Parameter 1 must be of type TreePath");
		}

		path.getPath().forEach(function(node){
			node.setExpanded(true);
		});
	}

	this.collapseAllNodes = function(){
		root.setExpanded(false);

		root.getChildren().forEach(function(child){
			TreeUtil.collapseNode(child);
		});
	}

	this.setContainer = function(_container){
		if(TreeUtil.isDOM(_container)){
			container = _container;
		}else{
			_container = document.querySelector(_container);

			if(_container instanceof Array){
				_container = _container[0];
			}

			if(!TreeUtil.isDOM(_container)){
				throw new Error("Parameter 1 must be either DOM-Object or CSS-QuerySelector (#, .)");
			}
		}
	}

	this.getContainer = function(){
		return container;
	}

	this.setOptions = function(_options){
		if(typeof _options === "object"){
			options = _options;
		}
	}

	this.changeOption = function(option, value){
		options[option] = value;
	}

	this.getOptions = function(){
		return options;
	}

	// TODO: set selected key: up down; expand right; collapse left; enter: open;
	this.getSelectedNodes = function(){
		return TreeUtil.getSelectedNodesForNode(root);
	}

	this.reload = function(){
		if(container == null){
			console.warn("No container specified");
			return;
		}

		container.classList.add("tj_container");

		var cnt = document.createElement("ul");

		if(TreeUtil.getProperty(options, "show_root", true)){
			cnt.appendChild(renderNode(root));
		}else{
			root.getChildren().forEach(function(child){
				cnt.appendChild(renderNode(child));
			});
		}

		container.innerHTML = "";
		container.appendChild(cnt);
	}

	function renderNode(node){
		var li_outer = document.createElement("li");
		var span_desc = document.createElement("span");
		span_desc.className = "tj_description";
		span_desc.tj_node = node;

		if(!node.isEnabled()){
			li_outer.setAttribute("disabled", "");
			node.setExpanded(false);
			node.setSelected(false);
		}
		
		if(node.isSelected()){
			span_desc.classList.add("selected");
		}

		span_desc.addEventListener("click", function(e){
			var cur_el = e.target;

			while(typeof cur_el.tj_node === "undefined" || cur_el.classList.contains("tj_container")){
				cur_el = cur_el.parentElement;
			}

			var node_cur = cur_el.tj_node;

			if(typeof node_cur === "undefined"){
				return;
			}

			if(node_cur.isEnabled()){
				if(e.ctrlKey == false){
					if(!node_cur.isLeaf()){
						node_cur.toggleExpanded();
						self.reload();
					}else{
						node_cur.open();
					}

					node_cur.on("click")(e, node_cur);
				}


				if(e.ctrlKey == true){
					node_cur.toggleSelected();
					self.reload();
				}else{
					var rt = node_cur.getRoot();

					if(rt instanceof TreeNode){
						TreeUtil.getSelectedNodesForNode(rt).forEach(function(_nd){
							_nd.setSelected(false);
						});
					}
					node_cur.setSelected(true);

					self.reload();
				}
			}
		});

		span_desc.addEventListener("contextmenu", function(e){
			var cur_el = e.target;

			while(typeof cur_el.tj_node === "undefined" || cur_el.classList.contains("tj_container")){
				cur_el = cur_el.parentElement;
			}

			var node_cur = cur_el.tj_node;

			if(typeof node_cur === "undefined"){
				return;
			}

			if(typeof node_cur.getListener("contextmenu") !== "undefined"){
				node_cur.on("contextmenu")(e, node_cur);
				e.preventDefault();
			}else if(typeof TreeConfig.context_menu === "function"){
				TreeConfig.context_menu(e, node_cur);
				e.preventDefault();
			}
		});

		if(node.isLeaf() && !TreeUtil.getProperty(node.getOptions(), "forceParent", false)){
			var ret = '';
			var icon = TreeUtil.getProperty(node.getOptions(), "icon", "");
			if(icon != ""){
				ret += '<span class="tj_icon">' + icon + '</span>';
			}else if((icon = TreeUtil.getProperty(options, "leaf_icon", "")) != ""){
				ret += '<span class="tj_icon">' + icon + '</span>';
			}else{
				ret += '<span class="tj_icon">' + TreeConfig.leaf_icon + '</span>';
			}

			span_desc.innerHTML = ret + node.toString() + "</span>";
			span_desc.classList.add("tj_leaf");

			li_outer.appendChild(span_desc);
		}else{
			var ret = '';
			if(node.isExpanded()){
				ret += '<span class="tj_mod_icon">' + TreeConfig.open_icon + '</span>';
			}else{
				ret+= '<span class="tj_mod_icon">' + TreeConfig.close_icon + '</span>';
			}

			var icon = TreeUtil.getProperty(node.getOptions(), "icon", "");
			if(icon != ""){
				ret += '<span class="tj_icon">' + icon + '</span>';
			}else if((icon = TreeUtil.getProperty(options, "parent_icon", "")) != ""){
				ret += '<span class="tj_icon">' + icon + '</span>';
			}else{
				ret += '<span class="tj_icon">' + TreeConfig.parent_icon + '</span>';
			}

			span_desc.innerHTML = ret + node.toString() + '</span>';

			li_outer.appendChild(span_desc);

			if(node.isExpanded()){
				var ul_container = document.createElement("ul");

				node.getChildren().forEach(function(child){
					ul_container.appendChild(renderNode(child));
				});

				li_outer.appendChild(ul_container)
			}
		}

		return li_outer;
	}

	if(typeof container !== "undefined")
		this.reload();
}

function TreeNode(userObject, options){
	var children = new Array();
	var self = this;
	var events = new Array();

	var expanded = true;
	var enabled = true;
	var selected = false;

	/*
	* Konstruktor
	*/
	if(userObject){
		if(typeof userObject !== "string" && typeof userObject.toString !== "function"){
			throw new Error("Parameter 1 must be of type String or Object, where it must have the function toString()");
		}
	}else{
		userObject = "";
	}

	if(!options || typeof options !== "object"){
		options = {};
	}else{
		expanded = TreeUtil.getProperty(options, "expanded", true);
		enabled = TreeUtil.getProperty(options, "enabled", true);
		selected = TreeUtil.getProperty(options, "selected", false);
	}

	/*
	* Methods
	*/
	this.addChild = function(node){
		if(!TreeUtil.getProperty(options, "allowsChildren", true)){
			console.warn("Option allowsChildren is set to false, no child added");
			return;
		}

		if(node instanceof TreeNode){
			children.push(node);

			//Konstante hinzufügen (workaround)
			Object.defineProperty(node, "parent", {
				value: this,
				writable: false,
				enumerable: true,
				configurable: true
			});
		}else{
			throw new Error("Parameter 1 must be of type TreeNode");
		}
	}

	this.removeChildPos = function(pos){
		if(typeof children[pos] !== "undefined"){
			if(typeof children[pos] !== "undefined"){
				children.splice(pos, 1);
			}
		}
	}

	this.removeChild = function(node){
		if(!(node instanceof TreeNode)){
			throw new Error("Parameter 1 must be of type TreeNode");
		}

		this.removeChildPos(this.getIndexOfChild(node));
	}

	this.getChildren = function(){
		return children;
	}

	this.getChildCount = function(){
		return children.length;
	}

	this.getIndexOfChild = function(node){
		for(var i = 0; i < children.length; i++){
			if(children[i].equals(node)){
				return i;
			}
		}

		return -1;
	}

	this.getRoot = function(){
		var node = this;

		while(typeof node.parent !== "undefined"){
			node = node.parent;
		}

		return node;
	}

	this.setUserObject = function(_userObject){
		if(!(typeof _userObject === "string") || typeof _userObject.toString !== "function"){
			throw new Error("Parameter 1 must be of type String or Object, where it must have the function toString()");
		}else{
			userObject = _userObject;
		}
	}

	this.getUserObject = function(){
		return userObject;
	}

	this.setOptions = function(_options){
		if(typeof _options === "object"){
			options = _options;
		}
	}

	this.changeOption = function(option, value){
		options[option] = value;
	}

	this.getOptions = function(){
		return options;
	}

	this.isLeaf = function(){
		return (children.length == 0);
	}

	this.setExpanded = function(_expanded){
		if(this.isLeaf()){
			return;
		}

		if(typeof _expanded === "boolean"){
			if(expanded == _expanded){
				return;
			}

			expanded = _expanded;

			if(_expanded){
				this.on("expand")(this);
			}else{
				this.on("collapse")(this);
			}

			this.on("toggle_expanded")(this);
		}
	}

	this.toggleExpanded = function(){
		if(expanded){
			this.setExpanded(false);
		}else{
			this.setExpanded(true);
		}
	};

	this.isExpanded = function(){
		if(this.isLeaf()){
			return true;
		}else{
			return expanded;
		}
	}

	this.setEnabled = function(_enabled){
		if(typeof _enabled === "boolean"){
			if(enabled == _enabled){
				return;
			}

			enabled = _enabled;

			if(_enabled){
				this.on("enable")(this);
			}else{
				this.on("disable")(this);
			}

			this.on("toggle_enabled")(this);
		}
	}

	this.toggleEnabled = function(){
		if(enabled){
			this.setEnabled(false);
		}else{
			this.setEnabled(true);
		}
	}

	this.isEnabled = function(){
		return enabled;
	}

	this.setSelected = function(_selected){
		if(typeof _selected !== "boolean"){
			return;
		}

		if(selected == _selected){
			return;
		}

		selected = _selected;

		if(_selected){
			this.on("select")(this);
		}else{
			this.on("deselect")(this);
		}

		this.on("toggle_selected")(this);
	}

	this.toggleSelected = function(){
		if(selected){
			this.setSelected(false);
		}else{
			this.setSelected(true);
		}
	}

	this.isSelected = function(){
		return selected;
	}

	this.open = function(){
		if(!this.isLeaf()){
			this.on("open")(this);
		}
	}

	this.on = function(ev, callback){
		if(typeof callback === "undefined"){
			if(typeof events[ev] !== "function"){
				return function(){};
			}else{
				return events[ev];
			}
		}

		if(typeof callback !== 'function'){
			throw new Error("Argument 2 must be of type function");
		}

		events[ev] = callback;
	}

	this.getListener = function(ev){
		return events[ev];
	}

	this.equals = function(node){
		if(node instanceof TreeNode){
			if(node.getUserObject() == userObject){
				return true;
			}
		}

		return false;
	}

	this.toString = function(){
		if(typeof userObject === "string"){
			return userObject;
		}else{
			return userObject.toString();
		}
	}
}

function TreePath(root, node){
	var nodes = new Array();

	this.setPath = function(root, node){
		nodes = new Array();

		while(typeof node !== "undefined" && !node.equals(root)){
			nodes.push(node);
			node = node.parent;
		}

		if(node.equals(root)){
			nodes.push(root);
		}else{
			nodes = new Array();
			throw new Error("Node is not contained in the tree of root");
		}

		nodes = nodes.reverse();

		return nodes;
	}

	this.getPath = function(){
		return nodes;
	}

	this.toString = function(){
		return nodes.join(" - ");
	}

	if(root instanceof TreeNode && node instanceof TreeNode){
		this.setPath(root, node);
	}
}

/*
* Util-Methods
*/
const TreeUtil = {
	default_leaf_icon: "<span>&#128441;</span>",
	default_parent_icon: "<span>&#128449;</span>",
	default_open_icon: "<span>&#9698;</span>",
	default_close_icon: "<span>&#9654;</span>",

	isDOM: function(obj){
		try {
			return obj instanceof HTMLElement;
		}
		catch(e){
			return (typeof obj==="object") &&
			(obj.nodeType===1) && (typeof obj.style === "object") &&
			(typeof obj.ownerDocument ==="object");
		}
	},

	getProperty: function(options, opt, def){
		if(typeof options[opt] === "undefined"){
			return def;
		}

		return options[opt];
	},

	expandNode: function(node){
		node.setExpanded(true);

		if(!node.isLeaf()){
			node.getChildren().forEach(function(child){
				TreeUtil.expandNode(child);
			});
		}
	},

	collapseNode: function(node){
		node.setExpanded(false);

		if(!node.isLeaf()){
			node.getChildren().forEach(function(child){
				TreeUtil.collapseNode(child);
			});
		}
	},

	getSelectedNodesForNode: function(node){
		if(!(node instanceof TreeNode)){
			throw new Error("Parameter 1 must be of type TreeNode");
		}

		var ret = new Array();

		if(node.isSelected()){
			ret.push(node);
		}

		node.getChildren().forEach(function(child){
			if(child.isSelected()){
				if(ret.indexOf(child) == -1){
					ret.push(child);
				}
			}

			if(!child.isLeaf()){
				TreeUtil.getSelectedNodesForNode(child).forEach(function(_node){
					if(ret.indexOf(_node) == -1){
						ret.push(_node);
					}
				});
			}
		});

		return ret;
	}
};

var TreeConfig = {
	leaf_icon: TreeUtil.default_leaf_icon,
	parent_icon: TreeUtil.default_parent_icon,
	open_icon: TreeUtil.default_open_icon,
	close_icon: TreeUtil.default_close_icon,
	context_menu: undefined
};
"""
