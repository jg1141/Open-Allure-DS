# add tabs and heading to openallure.cfg

cfgIn = open('..//openallure.cfg','r')
lines = cfgIn.readlines()
cfgIn.close
cfgOut = open('source//txt//openallure.rst','w')
cfgOut.write("""=====================
`openallure.cfg`
=====================

Modify this configuration file to suit your needs::

""")
for line in lines:
    cfgOut.write("    "+line)
cfgOut.close