index = """
<!DOCTYPE html>

<html>
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<link rel="stylesheet" type="text/css" href="resizable-style.css">
		<title>E3SM DIFF</title>

		<script src="resizable.js"></script>

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
                <input id="leftInput" type="file" multiple style="display: none;" >
                <input id="rightInput" type="file" multiple style="display: none;" >
                <button style="float: left;" onclick="document.getElementById('leftInput').click();">Open</button>
                <button style="float: right;" onclick="document.getElementById('rightInput').click();">Open</button>
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
				<div class="resizable-right" id="win12">
			    </div>
			</div>
		</div>
	</body>

	<script>

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

		});

		window.addEventListener("resize", () => {
			Resizable.activeContentWindows[0].changeSize(window.innerWidth, window.innerHeight);
			Resizable.activeContentWindows[0].childrenResize();
		});
                
        const leftInput = document.getElementById('leftInput');
        leftInput.addEventListener('change', (event) => {
            const fileList = event.target.files;
            //console.log(fileList);
            let text = "";
            for (let i = 0; i < fileList.length; i++) {
              text += fileList[i].name + "<br>";
            }
            
            alert(text);
        });
                
        const rightInput = document.getElementById('rightInput');
        rightInput.addEventListener('change', (event) => {
            const fileList = event.target.files;
            //console.log(fileList);
            let text = "";
            for (let i = 0; i < fileList.length; i++) {
              text += fileList[i].name + "<br>";
            }
            
            alert(text);
        });

	</script>

</html>
"""
