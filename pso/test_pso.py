from epics import PV

pvin = PV("2bmb:TomoScanStream:PSOCommand.BOUT")
pvout = PV("2bmb:TomoScanStream:PSOCommand.BINP")
pvin.put('PSOCONTROL X ON')
#pvin.put('DATAACQ X READ 0,2',wait=True)
#pvin.put('OPEN "TestFile.txt" FOR OUTPUT AS #1')
#pvin.put('PSOCONTROL X OFF')
print(pvout.get(as_string=True))
#pvin.put('WRITE #1, INTV:IGLOBAL(1)')
#pvin.put('CLOSE #1')
#164.54.113.102:8001