import os, subprocess, difflib

_legend = """
    <table class="diff" summary="Legends">
        <tr> <th colspan="2"> Legends </th> </tr>
        <tr> <td> <table border="" summary="Colors">
                      <tr><th> Colors </th> </tr>
                      <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr>
                      <tr><td class="diff_chg">Changed</td> </tr>
                      <tr><td class="diff_sub">Deleted</td> </tr>
                  </table></td>
             <td> <table border="" summary="Links">
                      <tr><th colspan="2"> Links </th> </tr>
                      <tr><td>(f)irst change</td> </tr>
                      <tr><td>(n)ext change</td> </tr>
                      <tr><td>(t)op</td> </tr>
                  </table></td> </tr>
    </table>"""

class E3SMHtmlDiff(difflib.HtmlDiff):
    pass

class Vimdiff():

    def __init__(self, left, right, workdir=None):

        self.workdir = workdir if workdir else os.getcwd()
        self.left = left
        self.right = right

    def get_data(self):

        data = {}
        ctype = "text/html"
        outfile = os.path.join(self.workdir, "vimdiff.html")

        try:
            lfile = open(self.left, 'U')
            llines = lfile.readlines()
            lfile.close()

            rfile = open(self.right, 'U')
            rlines = rfile.readlines()
            rfile.close()

            data["diffmain"] = difflib.HtmlDiff(wrapcolumn=50).make_table(llines, rlines, "<<<", ">>>")
            #data = difflib.E3SMHtmlDiff(wrapcolumn=50).make_file(llines, rlines, "<<<", ">>>")
            #data = difflib.E3SMHtmlDiff(wrapcolumn=50).make_difftable(llines, rlines, "<<<", ">>>")
            data["difflegend"] = _legend

        except FileNotFoundError as err:

            data = "File not found"

        #import pdb; pdb.set_trace()
        return (data, ctype)
