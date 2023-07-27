#coding=utf-8

from scanner import Scanner
from syntax_parser import SyntaxAnalyzer

if __name__ == "__main__":
    sc = Scanner()
    parser = SyntaxAnalyzer()

    text = '''
/*-------------------------------------------------------------------------------------------------
(C) COPYRIGHT 2016 FIRSTECH Co., Ltd. ALL RIGHTS RESERVED
This software and the associated documentation are confidential and proprietary to Firstech Co., Ltd. 
Project name : MRI Free Induction Release Sequence
File name : fir_seq.src
Author : Emily Crystal
Contacts : 
Date : 2023.07.07
File version : alpha0.0.1
Key words : 
File discription : 
Modified history : 
Date Author Version Details 
======================================================== 
 
--------------------------------------------------------------------------------------------------*/
#include "common.h" 
#include "grad.h" 
#include "tx.h" 
#include "rx.h" 
#include "mainctrl.h" 

double noViews= 25600; 
double viewBlock = 1; 
double samplePeriod=20; 
double noSamples =4096; 
double TR = 500;//ms 
double TE = 50000;//us 
double tsel90 =1000; //us 
double rf90Scale=10; 
double rxGain = 0.5;//db 
double ttxgatepost = 10; 
double ttxgatepre = 10; 
double tx_freq_offset_data = 0;//KHZ 
double tx_ph_offset_data = 0;//degree 
double trxgatepre = 10; 
double trxgatepost = 10; 
double rx_freq_offset_data = 0;//KHZ 
double rx_ph_offset_data = 0;//degree 
 
double trend = 1000; // us rx start acquire delay time
double preDiscard = 30;
double rf_tx_delay = 100; // us rf pulse tranmit delay time 
int rf_Shape_NO = 0;
double soft_pulse =0;
import TX 0 0 "my_rf_waveform.txt" my_rf_waveform

void main()
{ 
	MainctrlTrigger( viewBlock, noViews, TR); //
 
 	gradS:
 	{
 	}
 	gradR:
 	{
 	} 
 	gradP:
 	{
 	}
 	tx1:
 	{
		double delayTime_rf90_1; 
		tx_start:
 			TxChannelShapeSel(CHANNEL1,rf_Shape_NO); //
 			TxFreqOffsetReg(CHANNEL1,tx_freq_offset_data,KHZ); //
 			TxPhaseOffsetReg(CHANNEL1,tx_ph_offset_data); //
 			TxAttReg(CHANNEL1,rf90Scale); //
 			if(soft_pulse==0) TxHardPulseShape(CHANNEL1,tsel90); //
 			else TxChannelShapeSel(CHANNEL1,rf_Shape_NO); //
 			WaitTrigger(); //
 			delayTime_rf90_1 = rf_tx_delay; //
 			TimerCmp(delayTime_rf90_1,US); //
			TxStart(CHANNEL1,tsel90,ttxgatepre,ttxgatepost); //
 		goto tx_start;
	}
 	rx1:
 	{
		double fix_delaytime;
		double sample_period;
		double delayTime_c1; 
 		double sample_total;
		rx_start:
 			RxFreqOffsetReg(rx_freq_offset_data,KHZ); //
 			RxPhaseOffsetReg(rx_ph_offset_data); //
 			sample_total =preDiscard + noSamples; //
 			sample_period=RxChannelAcquirePara(samplePeriod,sample_total); //
 			RxGainReg(rxGain); //
 			fix_delaytime = TX_FILTER_DELAY-trxgatepre+rf_tx_delay; //
 			WaitTrigger(); //
 			delayTime_c1 = fix_delaytime+trend; //
 			TimerCmp(delayTime_c1,US); //
 			RxStart(1,trxgatepre,trxgatepost,sample_period); //
 		goto rx_start;
	}
}
    '''
    #sc.run(text)
    tokens = sc.parse(text)
    result = parser.parse(tokens)
    for item in result:
        print(repr(item))
    print(result)