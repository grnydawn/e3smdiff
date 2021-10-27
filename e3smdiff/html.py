index = """
<!DOCTYPE html>

<html>
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<link rel="stylesheet" type="text/css" href="resizable-style.css">
		<link rel="stylesheet" type="text/css" href="tree.css">
		<title>E3SM DIFF</title>

		<script src="resizable.js"></script>
		<script src="tree.js"></script>

		<style>

			#win5, #win14{
				background-color: #81A19F;
			}
			#win9, #win4{
				background-color: #BEEDEB;
			}
			#win12, #win6{
				background-color: #B4E0DE;
			}
			#win13, #win8{
				background-color: #A0C7C5;
			}

		</style>

	</head>

	<body>

		<div id="main">
			<div class="resizable-top" id="win1">
                <center><h1>E3SM DIFF</h1></center>
<!--
                <input id="leftInput" type="file" multiple style="display: none;" >
                <input id="rightInput" type="file" multiple style="display: none;" >
                <button style="float: left;" onclick="document.getElementById('leftInput').click();">Open</button>
                <button style="float: right;" onclick="document.getElementById('rightInput').click();">Open</button>
-->
			</div>
			<div class="resizable-bottom" id="win2">
				<div class="resizable-left" id="win3">
				    <div class="resizable-left" id="win4">
			        </div>
				    <div class="resizable-right" id="win5">
				        <div class="resizable-top" id="win6">
				            <div class="resizable-top" id="win7">
			                </div>
				            <div class="resizable-bottom" id="win8">
				                <div class="resizable-left" id="win9">
			                    </div>
				                <div class="resizable-right" id="win10">
			                    </div>
			                </div>
			            </div>
				        <div class="resizable-bottom" id="win11">
			            </div>
			        </div>
			    </div>
				<div class="resizable-right" id="win12" style="overflow-x: scroll;">
			    </div>
			</div>
		</div>
	</body>

	<script>

        // global variables

		var dummynode = new TreeNode("dummy");
		var leftTree = new TreeView(dummynode, "#win4");
		var rightTree = new TreeView(dummynode, "#win12");

        const leftInput = document.getElementById('leftInput');
        const rightInput = document.getElementById('rightInput');


        // functions
        function editDistance(s1, s2) {
          s1 = s1.toLowerCase();
          s2 = s2.toLowerCase();

          var costs = new Array();
          for (var i = 0; i <= s1.length; i++) {
            var lastValue = i;
            for (var j = 0; j <= s2.length; j++) {
              if (i == 0)
                costs[j] = j;
              else {
                if (j > 0) {
                  var newValue = costs[j - 1];
                  if (s1.charAt(i - 1) != s2.charAt(j - 1))
                    newValue = Math.min(Math.min(newValue, lastValue),
                      costs[j]) + 1;
                  costs[j - 1] = lastValue;
                  lastValue = newValue;
                }
              }
            }
            if (i > 0)
              costs[s2.length] = lastValue;
          }
          return costs[s2.length];
        }

        function similarity(s1, s2) {
          var longer = s1;
          var shorter = s2;
          if (s1.length < s2.length) {
            longer = s2;
            shorter = s1;
          }
          var longerLength = longer.length;
          if (longerLength == 0) {
            return 1.0;
          }
          return (longerLength - editDistance(longer, shorter)) / parseFloat(longerLength);
        }

        function pairing(left, right) {
            left.changeOption("pair", right);
            right.changeOption("pair", left);

            if (left.getChildCount() > 0) {
                var litems = left.getChildren();
            } else {
                var litems = [];
            }

            if (right.getChildCount() > 0) {
                var ritems = right.getChildren();
            } else {
                var ritems = [];
            }

            for (lidx in litems) {
                var litem = litems[lidx];
                var lname = litem.getUserObject();
                for (ridx in ritems) {
                    var ritem = ritems[ridx];
                    if (ritem.getUserObject() == lname) {
                        pairing(litem, ritem);
                        break;
                    }
                }
            }

/*
            // similrarity check for right nodes
            ritems.every(function (ritem) {
                if (!("pair" in ritem)) {
                    var rname = ritem.getUserObject();
                    litems.every(function (litem) {
                        if (!("pair" in litem)) {
                            var lname = litem.getUserObject();
                            if (similarity(rname, lname) > 0.8) {
                                //alert("test2");
                                pairing(litem, ritem);
                                return false;
                            } else {
                                return true;
                            }
                        }
                    });
                }
            });
*/
            // similrarity check for left nodes

        }

        function traverse(obj, depth) {
            var node = new TreeNode(obj["name"]);
            node.on("click", (e, n) => {

                if (!n.isLeaf()) {
                    isExpanded = n.isExpanded();
                }

                pair = n.getOptions()["pair"];
                if (typeof(pair) != "undefined") {

                    if (!pair.isLeaf()) {
                        pair.setExpanded(isExpanded);
                    }
                    pair.setSelected(true);

                    pairview = pair.getRoot().getOptions()["myview"];
                    pairview.reload();
                    pairsel = pairview.getSelectedNodes();
                    for ( pidx in pairsel) {
                        pairsel[pidx].setSelected(false);
                    }
                } else {
                    var myview = n.getRoot().getOptions()["myview"];
                    if (myview == leftTree) {
                        var pairview = rightTree;
                    } else {
                        var pairview = leftTree;
                    }
                    var pairsel = pairview.getSelectedNodes();
                    for ( pidx in pairsel) {
                        pairsel[pidx].setSelected(false);
                    }
                    pairview.reload();
                }
            });

            if ("children" in obj) {
                obj["children"].forEach(function (item, index) {
                  var child = traverse(item, depth+1);
                  node.addChild(child)  
                });

            }

            if (depth < 1) {
                node.setExpanded(true);
            } else {
                node.setExpanded(false);
            }

            return node;
        }

        function load_case(tree, response) {

            const c = JSON.parse(response);
            var depth = 0;
            root = traverse(c, depth);
            tree.setRoot(root)
            root.changeOption("myview", tree);

            // TODO: coloring non-diffed(black), different(red), same(blue)

            if (tree == leftTree) {
                root.changeOption("pairview", rightTree);
                var rightRoot = rightTree.getRoot()
                if ( rightRoot.getUserObject() != "dummy") {
                    pairing(root, rightRoot);
                }
            } else if (tree == rightTree) {
                root.changeOption("pairview", leftTree);
                var leftRoot = leftTree.getRoot()
                if ( leftRoot.getUserObject() != "dummy") {
                    pairing(leftRoot, root);
                }

            }

            tree.reload();
        }

        // listeners

		document.addEventListener("DOMContentLoaded", () => {
			//...
			document.getElementById("main").style.width = window.innerWidth + "px";
			document.getElementById("main").style.height = window.innerHeight + "px";

			var sizes = {
				"win1" : 0.1,
				"win3" : 0.83,
				"win4" : 0.2,
				"win6" : 0.8,
				"win7" : 0.1,
			};

			let resizerThickness = 4;
			Resizable.initialise("main", sizes, resizerThickness);
			//Resizable.initialise("main", {});

            // read case1 and case2
            var xhr = new XMLHttpRequest();
            xhr.open('GET', "/case1", true);
            xhr.responseType = 'text';
            xhr.onload = function() {
              var status = xhr.status;
              if (status === 200) {
                load_case(leftTree, xhr.responseText);
              } else {
                alert("load case1 failure");
              }
            };
            xhr.send();

            var xhr2 = new XMLHttpRequest();
            xhr2.open('GET', "/case2", true);
            xhr2.responseType = 'text';
            xhr2.onload = function() {
              var status = xhr2.status;
              if (status === 200) {
                load_case(rightTree, xhr2.responseText);
              } else {
                alert("load case2 failure");
              }
            };
            xhr2.send();
		});

		window.addEventListener("resize", () => {
			Resizable.activeContentWindows[0].changeSize(window.innerWidth, window.innerHeight);
			Resizable.activeContentWindows[0].childrenResize();
		});
	</script>

</html>
"""
