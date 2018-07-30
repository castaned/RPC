#!/usr/bin/env python

import re
import json
import sys
import getopt
from ROOT import *
from ROOT import gPad
from ROOT import TCanvas, TGraph
from ROOT import gROOT
from array import array
from numpy import median

import numpy as np
from scipy import stats

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def ratesEndcap_list():
  runNumfile = "data.json" #"output_rolls2018.json"
  with open(runNumfile) as dataf:
    rates1 = json.loads(dataf.read())
  rolls = ["_A","_B","_C"] #, "_D"]
  chambers = [
             "01","02","03","04","05","06","07","08","09",
        "10","11","12","13","14","15","16","17","18","19",
        "20","21","22","23","24","25","26","27","28","29",
        "30","31","32","33","34","35","36"
        ]
  ring = ["_R2", "_R3"]
  names = []
  rates = []
  for r in ring:
    for roll in rolls:
      #rates = []
      for c in chambers:
        try:
          #print r
          if float(rates1["rates"][endcapSection+r+"_CH"+c+roll]["ratesquarecm"]) == 0: continue
          rates.append(float(rates1["rates"][endcapSection+r+"_CH"+c+roll]["ratesquarecm"]))
          names.append(endcapSection+r+"_CH"+c+roll)
        except KeyError:
          continue
  #print sorted(names)
  return [names, rates]

def ratesWheel_lists():
  runNumfile = "data.json" #"output_rolls2018.json"
  with open(runNumfile) as dataf:
    rates1 = json.loads(dataf.read())
  wheels = ["0", "1", "2"]
  rolls = ["1", "2", "3", "4"]
  subrolls = ["in","out","+","-", "++", "--"]
  chambers = [
             "01","02","03","04","05","06",
             "07","08","09","10","11","12"]
  ring = ["Forward", "Middle", "Backward"]
  parameters = ["W"+wheelSection0+w+"_"+wheelSection+s+"_S"+c+"_"+ri for w in wheels
                for s in subrolls for c in chambers for ri in ring ]
                #if ( (w == "0") and (ri == "Forward") ) or ( w!="0" )]
  #W+2_RB2out_S10_Middle
  names = []
  rates = []
  for p in parameters:
    try:
      if float(rates1["rates"][p]["ratesquarecm"]) == 0: continue
      rates.append(float(rates1["rates"][p]["ratesquarecm"]))
      names.append(p)
    except KeyError:
      continue
  return [names, rates]

def etaWheel_lists():
  lines = []
  with open('WGeometry.out', 'rw') as shakes:
    for line in shakes:
      y = line.split(" glob(X,Y,Z)")
      lines.append(y)
  name = []
  etaMin = []
  etaMax = []
  etaAvg = []
  vMin = []
  vMax = []
  for line in lines:
    nameList = line[0]
    name.append(nameList.rstrip())
    # Informacion del first strip
    minEtaList0 = line[1].split("(")
    minEtaList1 = minEtaList0[1].split(",")   # Las entradas 0 y 1 son las coordenadas X y Y del strip
    minEtaList2 = minEtaList1[2].split(r")")  # La entrada 0 de esta lista es la coordenada Z del strip
    minX = float(minEtaList1[0])
    minY = float(minEtaList1[1])
    minZ = float(minEtaList2[0])
    v1 = TVector3(minX,minY,minZ)
    vMin.append(v1)
    eta1 = v1.Eta()
    etaMin.append(eta1)
    # Informacion del last strip
    maxEtaList0 = line[2].split("(")
    maxEtaList1 = maxEtaList0[1].split(",")   # Las entradas 0 y 1 son las coordenadas X y Y del strip
    maxEtaList2 = maxEtaList1[2].split(r")")  # La entrada 0 de esta lista es la coordenada Z del strip
    maxX = float(maxEtaList1[0])
    maxY = float(maxEtaList1[1])
    maxZ = float(maxEtaList2[0])
    v2 = TVector3(minX,minY,minZ)
    vMax.append(v2)
    eta2 = v2.Eta()
    etaMax.append(eta2)
    avgEtaValue = ( eta1 + eta2 ) /2
    etaAvg.append(avgEtaValue)

  List = [name, etaAvg]
  return List

def etaEndcap_list():
  lines = []
  with open('file.out', 'rw') as shakes:
    for line in shakes:
      y = line.split(",")
      lines.append(y)
  name = []
  etaMin = []
  etaMax = []
  etaAvg = []
  for line in lines:
    nameList = line[0]
    name.append(nameList.rstrip())
    minEtaList = line[3].split(" ")
    minEtaValue = [ x for x in minEtaList if is_number(x) ]
    etaMin.append(float(minEtaValue[0]))
    maxEtaList = line[4].split(" ")
    maxEtaValue = [ x for x in maxEtaList if is_number(x) ]
    etaMax.append(float(maxEtaValue[0]))
    avgEtaValue = (float(minEtaValue[0]) + float(maxEtaValue[0]) ) /2
    etaAvg.append(float(avgEtaValue))
  List = [name, etaAvg]
  return List

def intersect_list(etaList, ratesList):
  intersect = set(etaList[0]).intersection(ratesList[0])
  #print len(intersect)
  #newName  = []
  #newEta   = []
  #newRates = []
  dict0 = {}
  for i in intersect:
    etaIndex = etaList[0].index(i)
    rateIndex = ratesList[0].index(i)
    indict = { "eta": etaList[1][etaIndex],
               "rates":ratesList[1][rateIndex] }
    dict0[i] = indict
    #newName.append(i)
    #newEta.append(etaList[1][etaIndex])
    #newRates.append(ratesList[1][rateIndex])
  return dict0

def average_chambers(wheel, dictionary, X, Y):
  if wheel == 1:
    wheels = ["0", "1", "2"]
    rolls = ["1", "2", "3", "4"]
    subrolls = ["in","out","+","-", "++", "--"]
    chambers = [
               "01","02","03","04","05","06",
               "07","08","09","10","11","12"]
    ring = ["Forward", "Middle", "Backward"]
    for w in wheels:
      for s in subrolls:
        for ri in ring:
          eta = [v["eta"] for k, v in dictionary.items() 
                 for c in chambers if k == "W"+wheelSection0+w+"_"+wheelSection+s+"_S"+c+"_"+ri]
          rates = [v["rates"] for k, v in dictionary.items()
                 for c in chambers if k == "W"+wheelSection0+w+"_"+wheelSection+s+"_S"+c+"_"+ri]
          if rates and len(rates) != 1: 
  #          print max(set(rates), key=rates.count)
            #X.append( max(set(eta), key=eta.count)     )
            #Y.append( max(set(rates), key=rates.count) )
            X.append( median(eta)   )  #sum(eta)/len(eta) )
            Y.append( median(rates) )  #sum(rates)/len(rates) )

  elif wheel == 0:
    rolls = ["_A","_B","_C"] #, "_D"]
    chambers = [
               "01","02","03","04","05","06","07","08","09",
          "10","11","12","13","14","15","16","17","18","19",
          "20","21","22","23","24","25","26","27","28","29",
          "30","31","32","33","34","35","36"
          ]
    ring = ["_R2", "_R3"]
    for r in ring:
      for roll in rolls:
        eta = [v["eta"] for k, v in dictionary.items() for c in chambers if k == endcapSection+r+"_CH"+c+roll]
        rates = [v["rates"] for k, v in dictionary.items() for c in chambers if k == endcapSection+r+"_CH"+c+roll]
        if rates:# and len(rates) != 1:
          #X.append( max(set(eta), key=eta.count)     )
          #Y.append( max(set(rates), key=rates.count) )
          X.append( median(eta)   )  #sum(eta)/len(eta) )
          Y.append( median(rates) )  #sum(rates)/len(rates) )

def main():
  #if sys.argv[2]: print str(sys.argv[2])
  wheelEtaList = etaWheel_lists() #[names, eta] 
  #print "eta Wheel List Done"
  #print  len(wheelEtaList[0]), len(wheelEtaList[1])
  endcapEtaList = etaEndcap_list() #[names, eta] 
  #print "endcap eta list Done"
  #print  len(endcapEtaList[0]), len(endcapEtaList[1])
  wheelRatesList = ratesWheel_lists() #[names, rates]
  #print "wheel rates list Done" 
  #print len(wheelRatesList[0]), len(wheelRatesList[1])
  endcapRatesList = ratesEndcap_list() #[names, rates]
  #print "endcap rates list Done" 
  #print len(endcapRatesList[0]), len(endcapRatesList[1])

  #print "This is the problem"
  #print wheelEtaList
  #print wheelRatesList
  wheelIntersect = intersect_list(wheelEtaList,wheelRatesList) #name{eta, rates}
  #print "wheel eta/rate intersect Done"
  endcapIntersect = intersect_list(endcapEtaList,endcapRatesList) #name{eta, rates}
  #print "endcap eta/rate intersect Done"

  xW, yW = array( 'd' ), array( 'd' )
  xE, yE = array( 'd' ), array( 'd' )

  average_chambers(1, wheelIntersect,  xW, yW)
  print "Wheel Average Done"
  average_chambers(0, endcapIntersect, xE, yE)
  print "endcap average Done"

  #print len(xW), len(yW)
  #print len(xE), len(yE)

  return xW, yW, xE, yE

def eta_plot(X1W,Y1W,X2W,Y2W,X3W,Y3W,X4W,Y4W,X5W,Y5W,X6W,Y6W,X7W,Y7W,X8W,Y8W,
             X1E,Y1E,X2E,Y2E,X3E,Y3E,X4E,Y4E,X5E,Y5E,X6E,Y6E,X7E,Y7E,X8E,Y8E):

  print "------ Creating Wheel TGraph ----------"
  n1W = len(X1W)
  gr1 = TGraph(n1W,X1W,Y1W)
  gr1.SetLineColor( 2 )
  gr1.SetLineWidth( 4 )
  gr1.SetMarkerColor( 2 )
  gr1.SetMarkerStyle( 20 )
  gr1.SetMarkerSize( 1.5 )
  gr1.SetTitle( 'Layer 1 Wheel' )
  gr1.GetXaxis().SetTitle( '#eta' )
  gr1.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n2W = len(X2W)
  gr2 = TGraph(n2W,X2W,Y2W)
  gr2.SetLineColor( 3 )
  gr2.SetLineWidth( 5 )
  gr2.SetMarkerColor( 4 )
  gr2.SetMarkerStyle( 21 )
  gr2.SetMarkerSize( 1.5 )
  gr2.SetTitle( 'Layer 2 Wheel') 
  gr2.GetXaxis().SetTitle( '#eta' )
  gr2.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n3W = len(X3W)
  gr3 = TGraph(n3W,X3W,Y3W)
  gr3.SetLineColor( 4 )
  gr3.SetLineWidth( 6 )
  gr3.SetMarkerColor( 6 )
  gr3.SetMarkerStyle( 22 )
  gr3.SetMarkerSize( 1.5 )
  gr3.SetTitle( 'Layer 3 Wheel' )
  gr3.GetXaxis().SetTitle( '#eta' )
  gr3.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n4W = len(X4W)
  gr4 = TGraph(n4W,X4W,Y4W)
  gr4.SetLineColor( 5 )
  gr4.SetLineWidth( 7 )
  gr4.SetMarkerColor( 28 )
  gr4.SetMarkerStyle( 23 )
  gr4.SetMarkerSize( 1.5 )
  gr4.SetTitle( 'Layer 4 Wheel' )
  gr4.GetXaxis().SetTitle( '#eta' )
  gr4.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  print "------ Creating Endcap TGraph ----------"
  n1E = len(X1E)
  gr5 = TGraph(n1E,X1E,Y1E)
  gr5.SetLineColor( 2 )
  gr5.SetLineWidth( 4 )
  gr5.SetMarkerColor( 2 )
  gr5.SetMarkerStyle( 24 )
  gr5.SetMarkerSize( 1.5 )
  gr5.SetTitle( 'Layer 1 Endcap' )
  gr5.GetXaxis().SetTitle( '#eta' )
  gr5.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n2E = len(X2E)
  gr6 = TGraph(n2E,X2E,Y2E)
  gr6.SetLineColor( 3 )
  gr6.SetLineWidth( 5 )
  gr6.SetMarkerColor( 4 )
  gr6.SetMarkerStyle( 25 )
  gr6.SetMarkerSize( 1.5 )
  gr6.SetTitle( 'Layer 2 Endcap')
  gr6.GetXaxis().SetTitle( '#eta' )
  gr6.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n3E = len(X3E)
  gr7 = TGraph(n3E,X3E,Y3E)
  gr7.SetLineColor( 4 )
  gr7.SetLineWidth( 6 )
  gr7.SetMarkerColor( 6 )
  gr7.SetMarkerStyle( 26 )
  gr7.SetMarkerSize( 1.5 )
  gr7.SetTitle( 'Layer 3 Endcap' )
  gr7.GetXaxis().SetTitle( '#eta' )
  gr7.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n4E = len(X4E)
  gr8 = TGraph(n4E,X4E,Y4E)
  gr8.SetLineColor( 5 )
  gr8.SetLineWidth( 7 )
  gr8.SetMarkerColor( 28 )
  gr8.SetMarkerStyle( 32 )
  gr8.SetMarkerSize( 1.5 )
  gr8.SetTitle( 'Layer 4 Endcap' )
  gr8.GetXaxis().SetTitle( '#eta' )
  gr8.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  print "------ Creating Wheel TGraph ----------"
  n9W = len(X5W)
  gr9 = TGraph(n9W,X5W,Y5W)
  gr9.SetLineColor( 2 )
  gr9.SetLineWidth( 4 )
  gr9.SetMarkerColor( 2 )
  gr9.SetMarkerStyle( 20 )
  gr9.SetMarkerSize( 1.5 )
  gr9.SetTitle( 'Layer 1 Wheel' )
  gr9.GetXaxis().SetTitle( '#eta' )
  gr9.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n10W = len(X6W)
  gr10 = TGraph(n10W,X6W,Y6W)
  gr10.SetLineColor( 3 )
  gr10.SetLineWidth( 5 )
  gr10.SetMarkerColor( 4 )
  gr10.SetMarkerStyle( 21 )
  gr10.SetMarkerSize( 1.5 )
  gr10.SetTitle( 'Layer 2 Wheel')
  gr10.GetXaxis().SetTitle( '#eta' )
  gr10.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n11W = len(X7W)
  gr11 = TGraph(n11W,X7W,Y7W)
  gr11.SetLineColor( 4 )
  gr11.SetLineWidth( 6 )
  gr11.SetMarkerColor( 6 )
  gr11.SetMarkerStyle( 22 )
  gr11.SetMarkerSize( 1.5 )
  gr11.SetTitle( 'Layer 3 Wheel' )
  gr11.GetXaxis().SetTitle( '#eta' )
  gr11.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n12W = len(X8W)
  gr12 = TGraph(n12W,X8W,Y8W)
  gr12.SetLineColor( 5 )
  gr12.SetLineWidth( 7 )
  gr12.SetMarkerColor( 28 )
  gr12.SetMarkerStyle( 23 )
  gr12.SetMarkerSize( 1.5 )
  gr12.SetTitle( 'Layer 4 Wheel' )
  gr12.GetXaxis().SetTitle( '#eta' )
  gr12.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  print "------ Creating Endcap TGraph ----------"
  n13E = len(X5E)
  gr13 = TGraph(n13E,X5E,Y5E)
  gr13.SetLineColor( 2 )
  gr13.SetLineWidth( 4 )
  gr13.SetMarkerColor( 2 )
  gr13.SetMarkerStyle( 24 )
  gr13.SetMarkerSize( 1.5 )
  gr13.SetTitle( 'Layer 1 Endcap' )
  gr13.GetXaxis().SetTitle( '#eta' )
  gr13.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n14E = len(X6E)
  gr14 = TGraph(n14E,X6E,Y6E)
  gr14.SetLineColor( 3 )
  gr14.SetLineWidth( 5 )
  gr14.SetMarkerColor( 4 )
  gr14.SetMarkerStyle( 25 )
  gr14.SetMarkerSize( 1.5 )
  gr14.SetTitle( 'Layer 2 Endcap')
  gr14.GetXaxis().SetTitle( '#eta' )
  gr14.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n15E = len(X7E)
  gr15 = TGraph(n15E,X7E,Y7E)
  gr15.SetLineColor( 4 )
  gr15.SetLineWidth( 6 )
  gr15.SetMarkerColor( 6 )
  gr15.SetMarkerStyle( 26 )
  gr15.SetMarkerSize( 1.5 )
  gr15.SetTitle( 'Layer 3 Endcap' )
  gr15.GetXaxis().SetTitle( '#eta' )
  gr15.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )

  n16E = len(X8E)
  gr16 = TGraph(n16E,X8E,Y8E)
  gr16.SetLineColor( 5 )
  gr16.SetLineWidth( 7 )
  gr16.SetMarkerColor( 28 )
  gr16.SetMarkerStyle( 32 )
  gr16.SetMarkerSize( 1.5 )
  gr16.SetTitle( 'Layer 4 Endcap' )
  gr16.GetXaxis().SetTitle( '#eta' )
  gr16.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )


  print "----- Creating TCanvas -----"
  H = 800
  W = 800
  canv = TCanvas("c1", "Canvas", 800, 800)
  canv.Divide(2,2,0,0)
  maxY = 20
#*mg4.GetHistogram().GetMaximum()

  canv.cd(1)
  print " ------------ Creating TMultiGraph -----------"
  mg1 = TMultiGraph()
  mg1.Add(gr1,"AP")
  mg1.Add(gr5,"AP")
  mg1.Add(gr9,"AP")
  mg1.Add(gr13,"AP")
  mg1.Draw("a")
  mg1.SetTitle( 'Pseudorapidity Distribution')
  mg1.GetXaxis().SetTitle( '#eta' )
  mg1.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )
  mg1.SetMaximum(maxY)

  canv.cd(2)
  mg2 = TMultiGraph()
  mg2.Add(gr2,"AP")
  mg2.Add(gr6,"AP")
  mg2.Add(gr10,"AP")
  mg2.Add(gr14,"AP")
  mg2.Draw("a")
  mg2.SetTitle( 'Pseudorapidity Distribution')
  mg2.GetXaxis().SetTitle( '#eta' )
  mg2.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )
  mg2.SetMaximum(maxY)

  canv.cd(3)
  mg3 = TMultiGraph()
  mg3.Add(gr3,"AP")
  mg3.Add(gr7,"AP")
  mg3.Add(gr11,"AP")
  mg3.Add(gr15,"AP")
  mg3.Draw("a")
  mg3.SetTitle( 'Pseudorapidity Distribution')
  mg3.GetXaxis().SetTitle( '#eta' )
  mg3.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )
  mg3.SetMaximum(maxY)

  legend0 = TLegend(0.3, 0.7, .68, .9)
  legend0.SetNColumns(1)
  legend0.AddEntry(gr3, "Filled = Barrel", "p")
  legend0.AddEntry(gr7, "Open = Endcaps", "p")
  legend0.Draw("a same")

  canv.cd(4)
  mg4 = TMultiGraph()
  mg4.Add(gr4,"AP")
  mg4.Add(gr8,"AP")
  mg4.Add(gr12,"AP")
  mg4.Add(gr16,"AP")
  mg4.Draw("a")
  mg4.SetTitle( 'Pseudorapidity Distribution')
  mg4.GetXaxis().SetTitle( '#eta' )
  mg4.GetYaxis().SetTitle( 'RPC single hit rate (Hz/cm^{2})' )
  mg4.SetMaximum(maxY)

  legend = TLegend(0.3, 0.7, .68, .9)
  legend.SetNColumns(1)
  legend.AddEntry(gr1, "Layer 1", "p")
  legend.AddEntry(gr2, "Layer 2", "p")
  legend.AddEntry(gr3, "Layer 3", "p")
  legend.AddEntry(gr4, "Layer 4", "p")
  legend.Draw("a");  
  #canv.BuildLegend(0.3,0.7,0.68,0.9)

  canv.SaveAs("etaDistro.gif")

if __name__ == "__main__":
  endcapSectionList = ["RE-1", "RE-2", "RE-3", "RE-4", "RE+1", "RE+2", "RE+3", "RE+4"]
  wheelSectionList  = ["RB1", "RB2", "RB3", "RB4", "RB1", "RB2", "RB3", "RB4"]
  wheelSectionList0 = ["-", "-", "-", "-", "+", "+", "+", "+"]
  endcapSection = "RE+4"
  wheelSection  = "RB4"
  wheelSection0 = "-"
  try:
      opts, args = getopt.getopt(sys.argv[1:],"hi:o:",["ifile=","ofile="])
  except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
  for opt, arg in opts:
      if opt == '-h':
          print 'test.py -i <inputfile> -o <outputfile>'
          sys.exit()
      elif opt in ("-i", "--ifile"):
          endcapSection = str(arg)
      elif opt in ("-o", "--ofile"):
          wheelSection = str(arg)
  xW, yW = [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]
  xE, yE = [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]
  for i in range(8):
    endcapSection = endcapSectionList[i]
    wheelSection  = wheelSectionList[i]
    wheelSection0 = wheelSectionList0[i]
    xW[i], yW[i], xE[i], yE[i] = main()

  eta_plot(xW[0],yW[0],xW[1],yW[1],xW[2],yW[2],xW[3],yW[3],xW[4],yW[4],xW[5],yW[5],xW[6],yW[6],xW[7],yW[7],
           xE[0],yE[0],xE[1],yE[1],xE[2],yE[2],xE[3],yE[3],xE[4],yE[4],xE[5],yE[5],xE[6],yE[6],xE[7],yE[7],)
  
