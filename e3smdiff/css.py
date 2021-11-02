resizable = """
* {
  padding: 0;
  margin: 0;
  top: 0;
  left: 0;
}

.contentWindow{
  position: absolute;
  background-color: #B4E0DE;
}

.resizer{
  position: absolute;
  z-index: 100;
  background-color: #4E6160;
}

.verticalResizer{
  cursor: ns-resize;
}

.horizontalResizer{
  cursor: ew-resize;
}
"""

tree = """
.tj_container *{
	position: relative;
	box-sizing: border-box;
}

.tj_container ul{
	padding-left: 2em;
	list-style-type: none;
}

.tj_container > ul:first-of-type{
	padding: 0;
}

.tj_container li span.tj_description{
	cursor: pointer;
	padding: 2px 5px;
	display: block;
	border-radius: 2px;

	-webkit-touch-callout: none;
	-webkit-user-select: none;
	-khtml-user-select: none;
	-moz-user-select: none;
	-ms-user-select: none;
	user-select: none;

	text-align: left;
}

.tj_container li span.tj_description:hover{
	background-color: #ccc;
}

.tj_container li span.tj_mod_icon, .tj_container li span.tj_icon{
	margin-right: 0.5em;
	display: inline-block;
}

.tj_container li span.tj_mod_icon, .tj_container li span.tj_mod_icon *{
	width: 1em;
}

.tj_container li span.tj_description.tj_leaf{
	margin-left: 1.5em;
}

.tj_container li[disabled=""]{
	color: #b5b5b5;
}

.tj_container li[disabled=""]:hover span.tj_description{
	cursor: default;
	background-color: inherit;
}

.tj_container span.tj_description.selected{
	background-color: #2b2b2b;
	color: #fff;
}

.tj_container span.tj_description.selected:hover{
	background-color: #606060;
}
"""

diff_table = """
table.diff {font-family:Courier; border:medium;}

.diff_header {background-color:#e0e0e0}

td.diff_header {text-align:right}

.diff_next {background-color:#c0c0c0}

.diff_add {background-color:#aaffaa}

.diff_chg {background-color:#ffff77}

.diff_sub {background-color:#ffaaaa}

/*
.table th {
    position: relative;
}
.resizer {
    // Displayed at the right side of column
    position: absolute;
    top: 0;
    right: 0;
    width: 5px;
    cursor: col-resize;
    user-select: none;
}

.resizer:hover,
.resizing {
    border-right: 2px solid blue;
}
*/
"""
