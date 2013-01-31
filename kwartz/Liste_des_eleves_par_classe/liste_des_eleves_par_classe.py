#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Génère un pdf ave la liste des élèves par classe
argv 1 -> le fichier ldap
argv suivant -> la liste des classes
"""
import sys, re, locale, os
locale.setlocale(locale.LC_ALL, '')
from textwrap import dedent

ldap = sys.argv[1]
fichier = open(ldap, 'r')
c = fichier.read()

fichiertex = "liste_des_eleves_par_classe"
tex = open("%s.tex" % fichiertex, 'w')
entete = dedent(u"""
\\documentclass[francais,a4paper,notitlepage,11pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[francais]{babel}
\\usepackage{url}
\\usepackage{fancybox}
\\usepackage{vmargin}            % redefinir les marges
\\setmarginsrb{2cm}{2cm}{2cm}{2cm}{0cm}{0cm}{0cm}{0cm}
\\parindent 0em

\\begin{document}
"""[1:] )
tex.write(entete)

for classe in sys.argv[2:]:
    eleves = []
    pattrn = re.compile("^([^;]*;[^;]*;%s);" % classe, re.LOCALE|re.UNICODE|re.MULTILINE)
    for f in re.findall(pattrn, c):
        r = f.split(';')
        eleves.append((r[0], r[1].capitalize()))
    tex.write("\\begin{tabular}{|ll|}\n\\hline\n")
    tex.write("\\multicolumn{2}{|c|}{\\textbf{%s}} \\\\\n\\hline\n" % classe)
    #print sorted(eleves, key=lambda student: student[0])
    for f in sorted(eleves):
        tex.write("\\hline\n")
        tex.write("%s & %s \\\\\n" % (f[0], f[1]))
    tex.write("\\hline\n")
    tex.write("\\end{tabular}\n\\newpage\n\n")

tex.write("\\end{document}\n")
fichier.close()
tex.close()

try:
    #cmd = u'latex -interaction=nonstopmode %s.tex && dvips -o %.ps %s.dvi && ps2pdf %.ps' % (fichiertex, fichiertex, fichiertex, fichiertex)
    cmd = u'pdflatex -synctex=1 -interaction=nonstopmode %s.tex && evince %s.pdf' % (fichiertex, fichiertex)
    print u'Cmd > ' + cmd
    os.system(cmd)
except os.error as errno:
    print u"# Erreur : %s" % errno.errorcode[errno]
