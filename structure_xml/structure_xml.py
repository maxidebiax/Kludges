#!/usr/bin/python
# -*- coding: utf-8  -*-
# Permet de visualiser la structure du fichier profiles.xml de wpkg

#PyDot => graphviz
#http://networkx.lanl.gov/tutorial/tutorial.html
#http://docs.python.org/3.3/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt

# Parsing du fichier xml
G=nx.DiGraph()
tree = ET.parse('profiles.xml')
root = tree.getroot()
for child in root:
    nom = child.attrib['id']
    #print('======'+nom)
    G.add_node(nom, packages=[])
    for c in child:
        #print(c.tag, c.attrib)
        if c.tag == "depends":
            cible = c.attrib['profile-id']
            G.add_node(cible, packages=[])
            G.add_edge(nom, cible)
        elif c.tag == "package":
            val = c.attrib['package-id']
            G[nom]['packages'] =val
        """
            if G[nom].has_key('packages'):
                G[nom]['packages'].append(val)
            else:
                G[nom]['packages'] = [ val ]
        elif c.tag == "value":
            a = c.attrib['name']
            b = c.attrib['value']
            G[nom][a] = b
        """

# Dessinage
print(G['cdi'])
nx.draw_random(G)
plt.savefig("structure.png")
