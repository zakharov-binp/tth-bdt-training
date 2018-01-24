import itertools as it
import numpy as np
from root_numpy import root2array, stretch
from numpy.lib.recfunctions import append_fields
from itertools import product
from ROOT.Math import PtEtaPhiEVector,VectorUtil
import ROOT
import math , array

def load_data(inputPath,channelInTree,variables,criteria,testtruth,bdtType) :
    print variables
    my_cols_list=variables+['key','target','file']+criteria #,'tau_frWeight','lep1_frWeight','lep1_frWeight' trainVars(False)
    # if channel=='2lss_1tau' : my_cols_list=my_cols_list+['tau_frWeight','lep1_frWeight','lep2_frWeight']
    # those last are only for channels where selection is relaxed (2lss_1tau) === solve later
    data = pandas.DataFrame(columns=my_cols_list)
    if bdtType=="evtLevelTT_TTH" : keys=['ttHToNonbb','TTTo2L2Nu','TTToSemilepton']
    if bdtType=="evtLevelTTV_TTH" : keys=['ttHToNonbb','TTZToLLNuNu','TTWJetsToLNu']
    if bdtType=="all" : keys=['ttHToNonbb','TTZToLLNuNu','TTWJetsToLNu','TTTo2L2Nu','TTToSemilepton']
    if bdtType=="arun" : keys=['ttHToNonbb','TTZToLLNuNu','TTWJetsToLNu','TTTo2L2Nu','TTToSemilepton']
    for folderName in keys :
    	print (folderName, channelInTree)
    	if 'TTT' in folderName :
    		sampleName='TT'
    		target=0
    	if folderName=='ttHToNonbb' :
    		sampleName='signal'
    		target=1
    	if 'TTW' in folderName :
    		sampleName='TTW'
    		target=0
    	if 'TTZ' in folderName :
    		sampleName='TTZ'
    		target=0
    	inputTree = channelInTree+'/sel/evtntuple/'+sampleName+'/evtTree'
        if bdtType!="arun" :
        	if ('TTT' in folderName) or folderName=='ttHToNonbb' :
        		procP1=glob.glob(inputPath+"/"+folderName+"_fastsim_p1/"+folderName+"_fastsim_p1_forBDTtraining*OS_central_*.root")
        		procP2=glob.glob(inputPath+"/"+folderName+"_fastsim_p2/"+folderName+"_fastsim_p2_forBDTtraining*OS_central_*.root")
        		procP3=glob.glob(inputPath+"/"+folderName+"_fastsim_p3/"+folderName+"_fastsim_p3_forBDTtraining*OS_central_*.root")
        		list=procP1+procP2+procP3
        	else :
        		procP1=glob.glob(inputPath+"/"+folderName+"_fastsim/"+folderName+"_fastsim_forBDTtraining*OS_central_*.root")
        		list=procP1
        else : list=["arun_xml_2lss_1tau/ntuple_2lss_1tau_SS_OS_all.root"]
    	#print ("Date: ", time.asctime( time.localtime(time.time()) ))
    	for ii in range(0, len(list)) : #
    		#print (list[ii],inputTree)
    		try: tfile = ROOT.TFile(list[ii])
    		except :
    			#print "Doesn't exist"
    			#print ('file ', list[ii],' corrupt')
    			continue
    		try: tree = tfile.Get(inputTree)
    		except :
    			#print "Doesn't exist"
    			#print ('file ', list[ii],' corrupt')
    			continue
    		if tree is not None :
    			try:
    				chunk_arr = tree2array(tree) #,  start=start, stop = stop)
    			except :
    				#print "Doesn't exist"
    				#print ('file ', list[ii],' corrupt')
    				continue
    			else :
    				chunk_df = pandas.DataFrame(chunk_arr) #
    				#if ii ==0 : print (chunk_df.columns.values.tolist())
    				chunk_df['key']=folderName
    				chunk_df['target']=target
    				#chunk_df['file']=list[ii].split("_")[10]
    				if channel=="2lss_1tau" and bdtType!="arun" :
    					chunk_df["totalWeight"] = chunk_df["evtWeight"]*chunk_df['tau_frWeight']*chunk_df['lep1_frWeight']*chunk_df['lep2_frWeight']
    				if channel=="1l_2tau" : chunk_df["totalWeight"] = chunk_df.evtWeight
    				###########
    				if channel=="2lss_1tau"  and len(criteria)>0:
    					data=data.append(chunk_df.ix[chunk_df.failsTightChargeCut.values == 0], ignore_index=True)
    				else : #
    					#if 1>0 :
    					data=data.append(chunk_df, ignore_index=True)
    		else : print ("file "+list[ii]+"was empty")
    		tfile.Close()
    	if len(data) == 0 : continue
    	nS = len(data.ix[(data.target.values == 0) & (data.key.values==folderName)])
    	nB = len(data.ix[(data.target.values == 1) & (data.key.values==folderName)])
    	print folderName,"length of sig, bkg: ", nS, nB
    	if (channel=="1l_2tau" or channel=="2lss_1tau") and bdtType!="arun" :
    		nSthuth = len(data.ix[(data.target.values == 0) & (data.bWj1Wj2_isGenMatched.values==1) & (data.key.values==folderName)])
    		nBtruth = len(data.ix[(data.target.values == 1) & (data.bWj1Wj2_isGenMatched.values==1) & (data.key.values==folderName)])
    		nSthuthKin = len(data.ix[(data.target.values == 0) & (data.bWj1Wj2_isGenMatchedWithKinFit.values==1) & (data.key.values==folderName)])
    		nBtruthKin = len(data.ix[(data.target.values == 1) & (data.bWj1Wj2_isGenMatchedWithKinFit.values==1) & (data.key.values==folderName)])
    		nShadthuth = len(data.ix[(data.target.values == 0) & (data.hadtruth.values==1) & (data.key.values==folderName)])
    		nBhadtruth = len(data.ix[(data.target.values == 1) & (data.hadtruth.values==1) & (data.key.values==folderName)])
    		print "truth:              ", nSthuth, nBtruth
    		print "truth Kin:          ", nSthuthKin, nBtruthKin
    		print "hadtruth:           ", nShadthuth, nBhadtruth
    if folderName=='ttHToNonbb' : print (data.columns.values.tolist())
    n = len(data)
    nS = len(data.ix[data.target.values == 0])
    nB = len(data.ix[data.target.values == 1])
    print channelInTree," length of sig, bkg: ", nS, nB
    #print ("weigths", data.loc[data['target']==0]["totalWeight"].sum() , data.loc[data['target']==1]["totalWeight"].sum() )
    return data


def load_data_2l2t():
    keys=['ttH','ttbar','ttv']
    keystoDraw=['ttHToNonbb','TTToSemilepton','TTWJetsToLNu']
    treetoread="evtTree"
    weight="weight"
    sourceA="/home/arun/VHbbNtuples_8_0_x/CMSSW_8_1_0/src/Clusterization/"
    variables=["mva_ttv","mva_tt"]
    data = pandas.DataFrame(columns=variables+[weight,'key','target','totalWeight'])
    for nn, folderName in enumerate(keys) :
        tfile = ROOT.TFile(sourceA+folderName+"_2l2tau.root")
        tree = tfile.Get(treetoread)
        chunk_arr = tree2array(tree)
        chunk_df = pandas.DataFrame(chunk_arr)
        chunk_df['key']=keystoDraw[nn]
        chunk_df['totalWeight']=chunk_df[weight]
        chunk_df['target']=1 if folderName=='ttH' else 0
        data=data.append(chunk_df, ignore_index=True)
        print folderName,keystoDraw[nn]," length of sig, bkg: ", len(data.ix[data.key.values == keystoDraw[nn]])
    return data

def load_data_fullsim(inputPath,channelInTree,variables,criteria,testtruth,bdtType) :
    print variables
    my_cols_list=variables+['key','target','file']+criteria #,'tau_frWeight','lep1_frWeight','lep1_frWeight' trainVars(False)
    # if channel=='2lss_1tau' : my_cols_list=my_cols_list+['tau_frWeight','lep1_frWeight','lep2_frWeight']
    # those last are only for channels where selection is relaxed (2lss_1tau) === solve later
    sampleNames=['signal','TT','TTW','TTZ',"EWK","Rares"]
    samplesTT=['TTJets_DiLept',
    'TTJets_DiLept_ext1',
    'TTJets_SingleLeptFromT',
    'TTJets_SingleLeptFromT_ext1',
    'TTJets_SingleLeptFromTbar',
    'TTJets_SingleLeptFromTbar_ext1',
    'ST_tW_antitop_5f_inclusiveDecays',
    'ST_tW_top_5f_inclusiveDecays',
    'ST_s-channel_4f_leptonDecays',
    'ST_t-channel_antitop_4f_inclusiveDecays',
    'ST_t-channel_top_4f_inclusiveDecays', # + tH
    'THQ',
    'THW'
    ] # +6 fastsim
    samplesTTW=['TTWJetsToLNu_ext1','TTWJetsToLNu_ext2']
    samplesTTZ=['TTZToLL_M10_ext2', 'TTZToLL_M10_ext1', 'TTZToLL_M-1to10']
    samplesEWK=['DYJetsToLL_M-10to50',
    'DYJetsToLL_M-50_ext1',
    'DYJetsToLL_M-50_ext2',
    'WJetsToLNu',
    'WWTo2L2Nu',
    'ZZTo4L',
    'WZTo3LNu']
    samplesRares=['WGToLNuG_ext2',
    'TGJets',
    'TGJets_ext1',
    'TTTT',
    'TTWW',
    'WZZ',
    'ZGTo2LG',
    'WGToLNuG_ext1',
    'WWTo2L2Nu_DoubleScattering',
    'WWW_4F',
    'ZZZ',
    'TTGJets'
    'TTGJets_ext1',
    'tZq_ll_4f',
    'WpWpJJ_EWK-QCD']
    dataloc = pandas.DataFrame(columns=my_cols_list)
    if bdtType=="evtLevelTT_TTH" : keys=['ttHToNonbb','TTTo2L2Nu','TTToSemilepton']
    if bdtType=="evtLevelTTV_TTH" : keys=['ttHToNonbb','TTZToLLNuNu','TTWJetsToLNu']
    if bdtType=="all" : keys=['ttHToNonbb','TTZToLLNuNu','TTWJetsToLNu','TTTo2L2Nu','TTToSemilepton']
    if bdtType=="arun" : keys=['ttHToNonbb','TTZToLLNuNu','TTWJetsToLNu','TTTo2L2Nu','TTToSemilepton']
    for sampleName in sampleNames :
    	print (sampleName, channelInTree)
    	if sampleName=='TT' : #'TTT' in folderName :
    		folderNames=samplesTT
    		target=0
    	if sampleName=='signal' :
    		folderNames=['ttHJetToNonbb_M125_amcatnlo']
    		target=1
    	if sampleName=='TTW':
    		folderNames=samplesTTW
    		target=0
        if sampleName=='TTZ' :
    		folderNames=samplesTTZ
    		target=0
    	if sampleName=='EWK':
    		folderNames=samplesEWK
    		target=0
        if sampleName=='Rares' :
    		folderNames=samplesRares
    		target=0
    	inputTree = channelInTree+'/sel/evtntuple/'+sampleName+'/evtTree'
        #print (folderNames)
        list=[]
        for folderName in folderNames :
            # TGJets_forBDTtraining_lepSS_sumOS_central_1.root
            #procP1=glob.glob(inputPath+"/"+folderName+"/"+folderName+"_forBDTtraining*OS_central_*.root")
            #WWTo2L2Nu_DoubleScattering_Tight_lepSS_sumOS_central_1.root
            procP1=glob.glob(inputPath+"/"+folderName+"/"+folderName+"_Tight_*.root")
            list= list+procP1
            #if sampleName=='TT' : print (folderName)
    	#print (list)
    	for ii in range(0, len(list)) : #
    		#if sampleName=='TT' : print (list[ii])
    		try: tfile = ROOT.TFile(list[ii])
    		except :
    			#print "Doesn't exist"
    			#print ('file ', list[ii],' corrupt')
    			continue
    		try: tree = tfile.Get(inputTree)
    		except :
    			#print "Doesn't exist"
    			#print ('file ', list[ii],' corrupt')
    			continue
    		if tree is not None :
    			try:
    				chunk_arr = tree2array(tree) #,  start=start, stop = stop)
    			except :
    				#print "Doesn't exist"
    				#print ('file ', list[ii],' corrupt')
    				continue
    			else :
    				chunk_df = pandas.DataFrame(chunk_arr) #
    				#if ii ==0 : print (chunk_df.columns.values.tolist())
    				chunk_df['key']=folderName
    				chunk_df["target"]=target
    				chunk_df['proces']=sampleName
    				chunk_df["totalWeight"] = chunk_df.evtWeight
    				###########
    				if channel=="2lss_1tau"  and len(criteria)>0:
    					data=data.append(chunk_df.ix[chunk_df.failsTightChargeCut.values == 0], ignore_index=True)
    				else : #
    					#if 1>0 :
    					dataloc=dataloc.append(chunk_df, ignore_index=True)
    		else : print ("file "+list[ii]+"was empty")
    		tfile.Close()
    	if len(dataloc) == 0 : continue
    	nS = len(dataloc.ix[(dataloc.target.values == 0) & (dataloc.proces.values==sampleName)])
    	nB = len(dataloc.ix[(dataloc.target.values == 1) & (dataloc.proces.values==sampleName)])
    	print sampleName,"length of sig, bkg: ", nS, nB
    	if (channel=="1l_2tau" or channel=="2lss_1tau") and bdtType!="arun" :
    		nSthuth = len(dataloc.ix[(dataloc.target.values == 0) & (dataloc.bWj1Wj2_isGenMatched.values==1) & (dataloc.proces.values==sampleName)])
    		nBtruth = len(dataloc.ix[(dataloc.target.values == 1) & (dataloc.bWj1Wj2_isGenMatched.values==1) & (dataloc.proces.values==sampleName)])
    		nSthuthKin = len(dataloc.ix[(dataloc.target.values == 0) & (dataloc.bWj1Wj2_isGenMatchedWithKinFit.values==1) & (dataloc.proces.values==sampleName)])
    		nBtruthKin = len(dataloc.ix[(dataloc.target.values == 1) & (dataloc.bWj1Wj2_isGenMatchedWithKinFit.values==1) & (dataloc.proces.values==sampleName)])
    		nShadthuth = len(dataloc.ix[(dataloc.target.values == 0) & (dataloc.hadtruth.values==1) & (dataloc.proces.values==sampleName)])
    		nBhadtruth = len(dataloc.ix[(dataloc.target.values == 1) & (dataloc.hadtruth.values==1) & (dataloc.proces.values==sampleName)])
    		print "truth:              ", nSthuth, nBtruth
    		print "truth Kin:          ", nSthuthKin, nBtruthKin
    		print "hadtruth:           ", nShadthuth, nBhadtruth
    if 'ttHToNonbb' in folderName : print (dataloc.columns.values.tolist())
    n = len(dataloc)
    nS = len(dataloc.ix[dataloc.target.values == 0])
    nB = len(dataloc.ix[dataloc.target.values == 1])
    print sampleName," length of sig, bkg: ", nS, nB
    #print ("weigths", data.loc[data['target']==0]["totalWeight"].sum() , data.loc[data['target']==1]["totalWeight"].sum() )
    return dataloc


def load_data_xml (dataIn) :
    data=dataIn
    data["oldTrainTMVA_tt"]=-2.
    data["oldTrainTMVA_ttV"]=-2.
    for ii,ss in data.iterrows():
    	#if ii > 20 : break
    	clsTTreader = TMVA.Reader("Silent")
    	clsTTVreader = TMVA.Reader("Silent")
    	for feature in trainVarsTT(BDTvar) :
    		var= feature
    		if feature == "TMath::Max(TMath::Abs(lep1_eta),TMath::Abs(lep2_eta))" : var=  "max_lep_eta"
    		varVal=array.array('f',[ss[var]])
    		clsTTreader.AddVariable(str(feature),  varVal);
    	for feature in trainVarsTTV(BDTvar) :
    		var= feature
    		if feature == "TMath::Max(TMath::Abs(lep1_eta),TMath::Abs(lep2_eta))" : var=  "max_lep_eta"
    		varVal=array.array('f',[ss[var]])
    		clsTTVreader.AddVariable(str(feature),  varVal);
    	clsTTreader.BookMVA("BDT", "arun_xml_2lss_1tau/2lss_1tau_ttbar_BDTG.weights.xml")
    	clsTTVreader.BookMVA("BDT", "arun_xml_2lss_1tau/2lss_1tau_ttV_BDTG.weights.xml")
    	#for ii,ss in data.iterrows():
    	if ii % 1000 == 0 : print ("result TMVA ",ii, clsTTreader.EvaluateMVA("BDT"),clsTTVreader.EvaluateMVA("BDT"),data.loc[data.index[ii],trainVarsTT("oldTrainN")].values)
    	data.loc[data.index[ii],"oldTrainTMVA_tt"]=clsTTreader.EvaluateMVA("BDT")
    	data.loc[data.index[ii],"oldTrainTMVA_ttV"]=clsTTVreader.EvaluateMVA("BDT")
    data.to_csv('arun_xml_2lss_1tau/arun_xml_2lss_1tau_FromAnalysis.csv')
    return data

def reverse_colourmap(cmap, name = 'my_cmap_r'):
    reverse = []
    k = []
    for key in cmap._segmentdata:
        k.append(key)
        channel = cmap._segmentdata[key]
        data = []
        for t in channel:
            data.append((1-t[0],t[2],t[1]))
        reverse.append(sorted(data))
    LinearL = dict(zip(k,reverse))
    my_cmap_r = colors.LinearSegmentedColormap(name, LinearL)
    return my_cmap_r

def divisorGenerator(n):
    large_divisors = []
    for i in xrange(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i*i != n:
                if n / i <26 : large_divisors.append(n / i)
    for divisor in reversed(large_divisors):
        yield divisor

def doStackPlot(hTT,hTTH,hTTW,hEWK,hRares,name,label):
    print ("hTT, hTTH, hTTW, hEWK")
    print (hTT.Integral(),hTTH.Integral(),hTTW.Integral(),hEWK.Integral())
    hTT.SetFillColor( 17 );
    hTTH.SetFillColor( ROOT.kRed );
    hTTW.SetFillColor( 8 );
    hEWK.SetFillColor( 6 );
    hRares.SetFillColor( 65 );
    mc  = ROOT.THStack("mc","");
    mc.Add(hRares);
    mc.Add(hEWK);
    mc.Add(hTTW);
    mc.Add(hTTH);
    mc.Add( hTT );
    c4 = ROOT.TCanvas("c5","",500,500);
    c4.cd();
    c4.Divide(1,2,0,0);
    c4.cd(1)
    ROOT.gPad.SetLogy()
    #c5.SetLogy()
    ROOT.gPad.SetBottomMargin(0.001)
    ROOT.gPad.SetTopMargin(0.065)
    ROOT.gPad.SetRightMargin(0.01)
    ROOT.gPad.SetLeftMargin(0.12)
    #ROOT.gPad.SetLabelSize(.4, "XY")
    mc.Draw("HIST");
    mc.SetMaximum(15* mc.GetMaximum());
    mc.SetMinimum(max(0.04* mc.GetMinimum(),0.01));
    mc.GetYaxis().SetRangeUser(0.01,110);
    mc.GetHistogram().GetYaxis().SetTitle("Expected events/bin");
    mc.GetHistogram().GetXaxis().SetTitle("Bin in the bdt1#times bdt2 plane");
    mc.GetHistogram().GetXaxis().SetTitleSize(0.06);
    mc.GetHistogram().GetXaxis().SetLabelSize(.06); #SetTitleOffset(1.1);
    mc.GetHistogram().GetYaxis().SetTitleSize(0.06);
    mc.GetHistogram().GetYaxis().SetLabelSize(.06);
    l = ROOT.TLegend(0.16,0.6,0.3,0.9);
    l.AddEntry(hTTH  , "ttH", "f");
    l.AddEntry(hTTW  , "ttV"       , "f");
    l.AddEntry(hTT, "tt"        , "f");
    l.AddEntry(hRares, "rares"        , "f");
    l.AddEntry(hEWK, "EWK"        , "f");
    l.Draw();
    latex= ROOT.TLatex();
    latex.SetTextSize(0.065);
    latex.SetTextAlign(13);  #//align at top
    latex.SetTextFont(62);
    latex.DrawLatexNDC(.15,1.0,"CMS Simulation");
    latex.DrawLatexNDC(.8,1.0,"#it{36 fb^{-1}}");
    latex.DrawLatexNDC(.55,.8,label);
    #latex.DrawLatexNDC(.55,.9,BDTvar);
    c4.cd(2)
    ROOT.gStyle.SetHatchesSpacing(100)
    ROOT.gPad.SetLeftMargin(0.12)
    ROOT.gPad.SetBottomMargin(0.12)
    ROOT.gPad.SetTopMargin(0.001)
    ROOT.gPad.SetRightMargin(0.005)
    if not hTT.GetSumw2N() : hTT.Sumw2()
    h2=hTT.Clone()
    h2.Add(hTTW)
    hBKG1D=h2.Clone()
    h3=hTTH.Clone()
    h4=hTT.Clone()
    if not h2.GetSumw2N() : h2.Sumw2()
    if not h3.GetSumw2N() : h3.Sumw2()
    for binn in range(0,h2.GetNbinsX()+1) :
    	ratio=0
    	ratio3=0
    	if h2.GetBinContent(binn) >0 :
    		ratio=h2.GetBinError(binn)/h2.GetBinContent(binn)
    		h2.SetBinContent(binn,ratio)
    	if hBKG1D.GetBinContent(binn) > 0 :
    		ratio3=h3.GetBinContent(binn)/hBKG1D.GetBinContent(binn)
    		h3.SetBinContent(binn,ratio3)
    	if h4.GetBinContent(binn) > 0 : h4.SetBinContent(binn,h4.GetBinError(binn)/h4.GetBinContent(binn))
    	print (binn,ratio,ratio3)
    h2.SetLineWidth(3)
    h2.SetLineColor(2)
    h2.SetFillStyle(3690)
    h3.GetYaxis().SetRangeUser(0.01,1.0);
    h3.SetLineWidth(3)
    h3.SetFillStyle(3690)
    h3.SetLineColor(28)
    h4.SetLineWidth(3)
    h4.SetFillStyle(3690)
    h4.SetLineColor(6)
    h3.Draw("HIST")
    h3.GetYaxis().SetTitle("S/B");
    h3.GetXaxis().SetTitle("Bin in the bdt1#times bdt2 plane");
    h3.GetYaxis().SetTitleSize(0.06);
    h3.GetYaxis().SetLabelSize(.06)
    h3.GetXaxis().SetTitleSize(0.06);
    h3.GetXaxis().SetLabelSize(.06)
    l2 = ROOT.TLegend(0.16,0.77,0.4,0.98);
    l2.AddEntry(h3  , "S/B" , "l");
    l2.AddEntry(h2  , "ttV + tt err/cont", "l");
    l2.AddEntry(h4  , "tt err/cont", "l");
    l2.Draw("same");
    h2.Draw("HIST,SAME")
    h4.Draw("HIST,SAME")
    c4.Modified();
    c4.Update();
    print ("s/B in last bin (tight)", h3.GetNbinsX(), h3.GetBinContent(h3.GetNbinsX()), h3.GetBinContent(h3.GetNbinsX()-1), h2.GetBinContent(h3.GetNbinsX()))

    c4.SaveAs(name+".pdf")
    print ("saved",name+".pdf")

def finMaxMin(histSource) :
    file = TFile(source+".root","READ");
    file.cd()
    hSum = TH1F()
    for keyO in file.GetListOfKeys() :
       obj =  keyO.ReadObj()
       if type(obj) is not TH1F : continue
       hSumDumb = obj.Clone()
       if not hSum.Integral()>0 : hSum=hSumDumb
       else : hSum.Add(hSumDumb)
    return [[hSum.FindFirstBinAbove(0.0),  hSum.FindLastBinAbove (0.0)],
            [hSum.GetBinCenter(hSum.FindFirstBinAbove(0.0)),  hSum.GetBinCenter(hSum.FindLastBinAbove (0.0))]]

def getQuantiles(histoP,ntarget,xmax) :
    c = ROOT.TCanvas("c1","",600,600)
    histoP.Scale(1./histoP.Integral());
    histoP.GetCumulative().Draw();
    histoP.GetXaxis().SetRangeUser(0.,1.)
    histoP.GetYaxis().SetRangeUser(0.,1.)
    histoP.SetMinimum(0.0)
    xq= array.array('d', [0.] * (ntarget+1)) #[ii/nq for i in range(0,nq-1)] #np.empty(nq+1, dtype=object)
    yq= array.array('d', [0.] * (ntarget+1)) # [0]*nq #np.empty(nq+1, dtype=object)
    yqbin= array.array('d', [0.] * (ntarget+2))
    for  ii in range(0,ntarget) : xq[ii]=(float(ii)/(ntarget))
    xq[ntarget]=0.999999999
    histoP.GetQuantiles(ntarget,yq,xq)
    line = [None for point in range(ntarget)]
    line2 = [None for point in range(ntarget)]
    for  jj in range(0,ntarget) :
			line[jj] = ROOT.TLine(0,xq[jj],yq[jj],xq[jj]);
			line[jj].SetLineColor(ROOT.kRed);
			line[jj].Draw("same")
			#
			line2[jj] = ROOT.TLine(yq[jj],0,yq[jj],xq[jj]);
			line2[jj].SetLineColor(ROOT.kRed);
			line2[jj].Draw("same")
			print (xq[jj],yq[jj])
    #yq[ntarget]=xmax
    c.Modified();
    c.Update();
    yqbin[0]=0.0
    for  ii in range(1,ntarget+1) : yqbin[ii]=yq[ii-1]
    yqbin[ntarget+1]=xmax
    return yqbin

def GetRatio(histSource,namepdf) :
    file = TFile(histSource,"READ");
    file.cd()
    hSum = TH1F()
    h2 = TH1F()
    ratiohSum=1.
    ratiohSumP=1.
    ratio=1.
    ratioP=1.
    hTTi = TH1F()
    hTTHi = TH1F()
    hEWKi = TH1F()
    hTTWi = TH1F()
    hRaresi = TH1F()
    for keyO in file.GetListOfKeys() :
       obj =  keyO.ReadObj()
       if type(obj) is not TH1F : continue
       h2=obj.Clone()
       factor=1.
       if  not obj.GetSumw2N() : obj.Sumw2()
       if keyO.GetName() == "fakes_data"  or keyO.GetName() =="TTZ" or keyO.GetName() =="TTW" or keyO.GetName() =="TTWW" or keyO.GetName() == "EWK" :
           if not hSum.Integral()>0 : hSum=obj.Clone()
           else :
               hSum.Add(obj)
               print (keyO.GetName(),hSum.Integral())
       if keyO.GetName() == "fakes_data" :
           print ("last bin",keyO.GetName(),h2.GetBinContent(obj.GetNbinsX()),h2.GetBinContent(obj.GetNbinsX()-1),h2.Integral())
           if h2.GetBinContent(h2.GetNbinsX()) >0 : ratio=h2.GetBinError(h2.GetNbinsX())/h2.GetBinContent(h2.GetNbinsX())
           if obj.GetBinContent(h2.GetNbinsX()-1) >0 : ratioP=h2.GetBinError(h2.GetNbinsX()-1)/h2.GetBinContent(h2.GetNbinsX()-1)
       if h2.GetName() =="TTZ" or h2.GetName() =="TTW" :
            if not hTTWi.Integral()>0 : hTTWi=h2.Clone()
            else : hTTWi.Add(h2.Clone())
       if h2.GetName() == "fakes_data" : hTTi=h2.Clone()
       if h2.GetName() =="Rares" : hRaresi=h2.Clone()
       if h2.GetName() == "EWK" : hEWKi=h2.Clone()
       if h2.GetName() == "ttH_hww" or h2.GetName() == "ttH_hzz" or h2.GetName() ==  "ttH_htt" :
            if not hTTHi.Integral()>0 : hTTHi=h2.Clone()
            else : hTTHi.Add(h2.Clone())
    doStackPlot(hTTi,hTTHi,hTTWi,hEWKi,hRaresi,namepdf,"2D Map")
    print (namepdf+" created")
    if  not hSum.GetSumw2N() : hSum.Sumw2()
    if hSum.GetBinContent(hSum.GetNbinsX()) >0 :
            ratiohSum=hSum.GetBinError(hSum.GetNbinsX())/hSum.GetBinContent(hSum.GetNbinsX())
    if hSum.GetBinContent(hSum.GetNbinsX()-1) >0 : ratiohSumP=hSum.GetBinError(hSum.GetNbinsX()-1)/hSum.GetBinContent(hSum.GetNbinsX()-1)
    print (ratio,ratioP,ratiohSum,ratiohSumP)
    print (hSum.GetBinContent(hSum.GetNbinsX()))
    return [ratio,ratioP,ratiohSum,ratiohSumP]


def rebinRegular(histSource,nbin, BINtype,originalBinning,doplots,variables,bdtType) :
    minmax = finMaxMin(histSource)
    errOcontTTLast=[]
    errOcontTTPLast=[]
    errOcontSUMLast=[]
    errOcontSUMPLast=[]
    #
    errTTLast=[]
    contTTLast=[]
    errSUMLast=[]
    contSUMLast=[]
    #
    realbins=[]
    xminbin=[]
    xmaxbin=[]
    xmaxLbin=[]
    #
    lastQuant=[]
    xmaxQuant=[]
    xminQuant=[]
    #
    if BINtype=="ranged" :
        xmin=minmax[1][0]
        xmax=minmax[1][1]
        xmindef=minmax[1][0]
        xmaxdef=minmax[1][1]
    else :
        xmin=0.0
        xmax=1.0
        xmaxdef=minmax[1][1]
        xmindef=minmax[1][0]
    for nn,nbins in enumerate(nbin) :
        file = TFile(histSource+".root","READ");
        file.cd()
        histograms=[]
        histograms2=[]
        h2 = TH1F()
        hSum = TH1F()
        hFakes = TH1F()
        hSumAll = TH1F()
        ratiohSum=1.
        ratiohSumP=1.
        for nkey, keyO in enumerate(file.GetListOfKeys()) :
           #print keyO
           obj =  keyO.ReadObj()
           if type(obj) is not TH1F : continue
           h2 = obj.Clone();
           factor=1.
           if  not h2.GetSumw2N() : h2.Sumw2()
           if  not hSum.GetSumw2N() : hSum.Sumw2()
           histograms.append(h2.Clone()) # [nkey]=h2.Clone()  #=histograms+[h2]
           if keyO.GetName() == "fakes_data" or keyO.GetName() =="TTZ" or keyO.GetName() =="TTW" or keyO.GetName() =="TTWW" or keyO.GetName() == "EWK" :
               hSumDumb = obj # h2_rebin #
               if not hSum.Integral()>0 : hSum=hSumDumb.Clone()
               else : hSum.Add(hSumDumb)
               if keyO.GetName() == "fakes_data" : hFakes=hSumDumb.Clone()
           if keyO.GetName() == "fakes_data" or keyO.GetName() =="TTZ" or keyO.GetName() =="TTW" or keyO.GetName() =="TTWW" or keyO.GetName() == "EWK" or keyO.GetName() == "tH" or keyO.GetName() == "Rares" :
               hSumDumb2 = obj # h2_rebin #
               if not hSumAll.Integral()>0 : hSumAll=hSumDumb2.Clone()
               else : hSumAll.Add(hSumDumb)
        #################################################
        ### rebin and  write the histograms
        if BINtype=="none" : name=histSource+"_"+str(nbins)+"bins_none.root"
        if BINtype=="regular" : name=histSource+"_"+str(nbins)+"bins.root"
        if BINtype=="ranged" : name=histSource+"_"+str(nbins)+"bins_ranged.root"
        if BINtype=="quantiles" :
            ## do the quantiles in the sum o BKG
            name=histSource+"_"+str(nbins+1)+"bins_quantiles.root"
            #nbinsQuant=getQuantiles(hSum,nbins,xmax)
            nbinsQuant=getQuantiles(hFakes,nbins,xmax)
            #print (nbins+1,nbinsQuant)
            #nbinsQuant=getQuantiles(hSumAll,nbins,xmax)
            #print ("quantiles",nbins,nbinsQuant,nbinsQuant[nbins],nbinsQuant[nbins-1],nbinsQuant[nbins-2])
            xmaxLbin=xmaxLbin+[nbinsQuant[nbins-1]]
        fileOut  = TFile(name, "recreate");
        hTTi = TH1F()
        hTTHi = TH1F()
        hEWKi = TH1F()
        hTTWi = TH1F()
        hRaresi = TH1F()
        histo = TH1F()
        for nn, histogram in enumerate(histograms) :
            histogramCopy=histogram.Clone()
            nameHisto=histogramCopy.GetName()
            histogram.SetName(histogramCopy.GetName()+"_"+str(nn)+BINtype)
            histogramCopy.SetName(histogramCopy.GetName()+"Copy_"+str(nn)+BINtype)
            if histogramCopy.GetName() == "fakes_data" or histogramCopy.GetName() =="TTZ" or histogramCopy.GetName() =="TTW" or histogramCopy.GetName() =="TTWW" or histogramCopy.GetName() == "EWK" :
                print ("not rebinned",histogramCopy.GetName(),histogramCopy.Integral())
            if BINtype=="none" :
                histo=histogramCopy.Clone()
                histo.SetName(nameHisto)
            elif BINtype=="ranged" or BINtype=="regular" :
                histo= TH1F( nameHisto, nameHisto , nbins , xmin , xmax)
            elif BINtype=="quantiles" :
                histo=TH1F( nameHisto, nameHisto , nbins+1 , nbinsQuant)
            #if not histo.GetSumw2N() : histo.Sumw2()
            #print histogramCopy.GetNbinsX()
            #if not BINtype=="none" :
            #print ("fine binning",histogramCopy.GetXaxis().GetBinLowEdge(1),histogramCopy.GetXaxis().GetBinLowEdge(2))
            #if bdtType=="1B" and nbins ==4 : print ("quantiles",histo.GetXaxis().GetBinLowEdge(1),histo.GetXaxis().GetBinLowEdge(2),histo.GetXaxis().GetBinLowEdge(3),histo.GetXaxis().GetBinLowEdge(4),histo.GetXaxis().GetBinLowEdge(5))
            for place in range(1,histogramCopy.GetNbinsX() + 1) :
                content =      histogramCopy.GetBinContent(place)
                binErrorCopy = histogramCopy.GetBinError(place);
                newbin =       histo.FindBin(histogramCopy.GetBinCenter(place))
                binError =     histo.GetBinError(newbin);
                histo.SetBinContent(newbin, histo.GetBinContent(newbin)+content)
                #if histo.GetName() == "ttH_hww" or histo.GetName() == "ttH_hzz" or histo.GetName() ==  "ttH_htt" : print (content,newbin)
                histogram.SetBinError(newbin,sqrt(binError*binError+binErrorCopy*binErrorCopy))
            if not histogram.GetSumw2N() : histogram.Sumw2()
            #histo.SetBinErrorOption(1) # https://root.cern.ch/doc/v608/classTH1.html#ac6e38c12259ab72c0d574614ee5a61c7
            if histogramCopy.GetName() == "fakes_data" or histogramCopy.GetName() =="TTZ" or histogramCopy.GetName() =="TTW" or histogramCopy.GetName() =="TTWW" or histogramCopy.GetName() == "EWK" :
                print ("rebinned",histo.GetName(),histo.Integral())
            histo.Write()
            #print (histo.GetName(),histo.Integral())
            #######################
            if histo.GetName() == "fakes_data" :
                ratio=1.
                ratioP=1.
                hTTi=histo.Clone()
                hTTi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                if histo.GetBinContent(histo.GetNbinsX()) >0 : ratio=histo.GetBinError(histo.GetNbinsX())/histo.GetBinContent(histo.GetNbinsX())
                if histo.GetBinContent(histo.GetNbinsX()-1) >0 : ratioP=histo.GetBinError(histo.GetNbinsX()-1)/histo.GetBinContent(histo.GetNbinsX()-1)
                errOcontTTLast=errOcontTTLast+[ratio] if ratio<1.01 else errOcontTTLast+[1.0]
                errOcontTTPLast=errOcontTTPLast+[ratioP] if ratioP<1.01 else errOcontTTPLast+[1.0]
                errTTLast=errTTLast+[histo.GetBinError(histo.GetNbinsX())]
                contTTLast=contTTLast+[histo.GetBinContent(histo.GetNbinsX())]
            if histo.GetName() =="TTZ" or histo.GetName() =="TTW" :
                if not hTTWi.Integral()>0 :
                    hTTWi=histo.Clone()
                    hTTWi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                else : hTTWi.Add(histo.Clone())
            if histo.GetName() =="Rares" :
                hRaresi=histo.Clone()
                hRaresi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
            if histo.GetName() == "EWK" :
                hEWKi=histo.Clone()
                hEWKi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
            if histo.GetName() == "ttH_hww" or histo.GetName() == "ttH_hzz" or histo.GetName() ==  "ttH_htt" :
                if not hTTHi.Integral()>0 :
                    hTTHi=histo.Clone()
                    hTTHi.SetName(histo.GetName()+"toplot_"+str(nn)+BINtype)
                else : hTTHi.Add(histo.Clone())
                #if histo.GetName() =="signal" : print ("TTH",histo.GetNbinsX())
                #if histo.GetName() =="TTZ" : print ("TTZ",histo.GetNbinsX())
                #if histo.GetName() =="TTW" : print ("TTW",histo.GetNbinsX())
                #if histo.GetName() =="EWK" : print ("EWK",histo.GetNbinsX())
                #if histo.GetName() =="TTWW" : print ("TTWW",histo.GetNbinsX())
        fileOut.Write()
        print (name+" created")
        if doplots and bdtType=="1B":
            if nbins==4  :
                if BINtype=="none" : namepdf=histSource
                if BINtype=="regular" : namepdf=histSource+"_"+str(nbins)+"bins"
                if BINtype=="ranged" : namepdf=histSource+"_"+str(nbins)+"bins_ranged"
                if BINtype=="quantiles" :
                    namepdf=histSource+"_"+str(nbins+1)+"bins_quantiles"
                    label=str(nbins+1)+" bins "+BINtype+" "+variables+" "+bdtType
                else : label=str(nbins)+" bins "+BINtype+" "+variables+" "+bdtType
                doStackPlot(hTTi,hTTHi,hTTWi,hEWKi,hRaresi,namepdf,label)
                print (namepdf+" created")
        hSumCopy=hSum.Clone()
        hSumi = TH1F()
        if BINtype=="ranged" or BINtype=="regular" : hSumi = TH1F( "hSum", "hSum" , nbins , xmin , xmax)
        elif BINtype=="quantiles" : hSumi = TH1F( "hSum", "hSum" , nbins , nbinsQuant)
        if not hSumi.GetSumw2N() : hSumi.Sumw2()
        for place in range(1,hSumCopy.GetNbinsX() + 1) :
            content=hSumCopy.GetBinContent(place)
            newbin=hSumi.FindBin(hSumCopy.GetBinCenter(place))
            binErrorCopy = hSumCopy.GetBinError(place);
            binError = hSumi.GetBinError(newbin);
            hSumi.SetBinContent(newbin, hSumi.GetBinContent(newbin)+content)
            hSumi.SetBinError(newbin,sqrt(binError*binError+ binErrorCopy*binErrorCopy))
        hSumi.SetBinErrorOption(1)
        #if not hSum.GetSumw2N() : hSum.Sumw2()
        if hSumi.GetBinContent(hSumi.GetNbinsX()) >0 :
            ratiohSum=hSumi.GetBinError(hSumi.GetNbinsX())/hSumi.GetBinContent(hSumi.GetNbinsX())
        if hSumi.GetBinContent(hSumi.GetNbinsX()-1) >0 : ratiohSumP=hSumi.GetBinError(hSumi.GetNbinsX()-1)/hSumi.GetBinContent(hSumi.GetNbinsX()-1)
        errOcontSUMLast=errOcontSUMLast+[ratiohSum] if ratiohSum<1.001 else errOcontSUMLast+[1.0]
        errOcontSUMPLast=errOcontSUMPLast+[ratiohSumP] if ratiohSumP<1.001 else errOcontSUMPLast+[1.0]
        errSUMLast=errSUMLast+[hSumi.GetBinError(hSumi.GetNbinsX())]
        contSUMLast=contSUMLast+[hSumi.GetBinContent(hSumi.GetNbinsX())]
        if BINtype=="quantiles" :
            lastQuant=lastQuant+[nbinsQuant[nbins]]
            xmaxQuant=xmaxQuant+[xmaxdef]
            xminQuant=xminQuant+[xmindef]
    print ("min",xmindef,xmin)
    print ("max",xmaxdef,xmax)
    #print ("errOcont",errOcontTTLast)
    #print ("errOcont",errOcontSUMLast)
    return [errOcontTTLast,errOcontTTPLast,errOcontSUMLast,errOcontSUMPLast,lastQuant,xmaxQuant,xminQuant]
            #errTTLast,contTTLast,errSUMLast,contSUMLast]

def ReadLimits(bdtType,nbin, BINtype,originalBinning,local,nstart,ntarget):
    central=[]
    do1=[]
    do2=[]
    up1=[]
    up2=[]
    for nn,nbins in enumerate(nbin) :
        # ttH_2lss_1taumvaOutput_2lss_MEM_1D_nbin_9.log
        if nstart==0 : shapeVariable=options.variables+'_'+bdtType+'_nbin_'+str(nbins)
        else : shapeVariable=options.variables+'_from'+str(nstart)+'_to_'+str(nbins)
        if BINtype=="ranged" : shapeVariable=shapeVariable+"_ranged"
        if BINtype=="quantiles" : shapeVariable=shapeVariable+"_quantiles"
        datacardFile_output = os.path.join(local, "ttH_%s.log" % shapeVariable)
        if nn==0 :print  shapeVariable
        f = open(datacardFile_output, 'r+')
        lines = f.readlines() # get all lines as a list (array)
        for line in  lines:
          l = []
          tokens = line.split()
          if "Expected  2.5%"  in line : do2=do2+[float(tokens[4])]
          if "Expected 16.0%:" in line : do1=do1+[float(tokens[4])]
          if "Expected 50.0%:" in line : central=central+[float(tokens[4])]
          if "Expected 84.0%:" in line : up1=up1+[float(tokens[4])]
          if "Expected 97.5%:" in line : up2=up2+[float(tokens[4])]
    #print (shapeVariable,nbin)
    print (shapeVariable,central)
    #print do1
    return [central,do1,do2,up1,up2]