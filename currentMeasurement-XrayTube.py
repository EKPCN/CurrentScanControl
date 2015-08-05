#!/usr/bin/python

import serial
import time
import sys
import os
from time import gmtime, strftime
import re


#**********************************************
# directory names
#**********************************************
datadirectory = "/home/readout/pXar_output/20150615_M4521_p18_px204fw40"	#to complete
pXardir = "/home/readout/psiexpert/pxar"
#pXardir = "/home/readout/psiexpert/pxar-v1.7.4"
#pXardir = "/home/readout/psiexpert/pxar-v1.9.0"

#**************************************************************************
# Temperature, trim Vcal, Begin of run number in document name, used target
#**************************************************************************
temperature ='p18'
trimVcal = 35
runnrBegin = 70
target = 'Nd'

################################################################################################
desVoltage = 60;		#desired tube voltage in kV 				(2kV < x < 60kV and integer)
desCurrentBegin = 2;	#desired smallest current in mA at which the rate measurement will start
desCurrentEnd = 30;		#desired biggest current in mA at which the rate measurement will end
desCurrentStep = 4;		#distance of steps between the two borders (in mA)
################################################################################################


def testCurrent(int_current_mA):
	if(int_current_mA < 2 or int_current_mA > 80 or type(int_current_mA) != int):
		return False;
	return True;

def setCurrent(int_current_mA):
	if(testCurrent(int_current_mA) == False):
		print "Please type a integer variable between 2 and 80 mA for the current\n";
		sys.exit();
	string = 'SC:%02d\r' % int_current_mA;	#Produce right formatted command (carriage return at the end)
	#print string;
	port.write( string );	#Write string to port
	time.sleep(3); 					#Wait three seconds before sending new request
	counter = 1;
	while(True):
		answerCN = nominalCurrent();
		if(float(1000*int_current_mA) == float(answerCN)):
			break;
		if(counter == 3):			#After 3 unsuccesful requests the function will end 
			print "Could not set or receive nominal current\n";
			return False;
		counter = counter + 1;
		time.sleep(3);
	counter = 1;
	while(True):
		answerCA = actualCurrent();
		if(float(1000*int_current_mA) == float(answerCA)):
			break;
		if(counter == 5):			#After 5 unsuccesful requests the function will end 
			print "Can't receive actual current (after 5 tries)\n";
			return False;
		counter = counter + 1;
		time.sleep(3);
	print "Actual current has reached {0}mA".format(int_current_mA);
	return True;
	
def nominalCurrent():
	port.write( 'CN\r' );	#Request nominal current
	time.sleep(1);
	#answerCN = "*0000032000";
	answerCN = port.readline(12);
	answerCN = answerCN[1:];	#Delete * in the front of the answer
	return answerCN;

def actualCurrent():
	time.sleep(3);
	port.write( 'CA\r' );	#Request actual current
	time.sleep(1);
	#answerCA = "*0000032000";
	answerCA = port.readline(12);
	answerCA = answerCA[1:];
	return answerCA;


def testVoltage(int_voltage_kV):
	if(int_voltage_kV < 2 or int_voltage_kV > 60 or type(int_voltage_kV) != int):
		return False;
	return True;
	
def setVoltage(int_voltage_kV):
	if(testVoltage(int_voltage_kV) == False):
		print "Please type a integer variable between 2 and 60 kV for the voltage\n";
		sys.exit();
	string = 'SV:%02d\r' % int_voltage_kV;	#Produce right formatted command
	#print string;
	port.write( string );	#Write string to port
	time.sleep(3); 					#Wait three seconds before sending new request
	counter = 1;
	while(True):
		answerVN = nominalVoltage();
		if(float(1000*int_voltage_kV) == float(answerVN)):
			break;
		if(counter == 3):			#After 3 unsuccesful requests the function will end 
			print "Could not set or receive the nominal voltage\n";
			sys.exit();
		counter = counter + 1;
	counter = 1;
	while(True):
		answerVA = actualVoltage();
		if(float(1000*int_voltage_kV) == float(answerVA)):
			break;
		if(counter == 5):			#After 5 unsuccesful requests the function will end 
			print "Could not receive the actual voltage\n";
			sys.exit();
			#return False;
		counter = counter + 1;
	print "Actual voltage has reached {0}kV.".format(int_voltage_kV);
	return True;

def nominalVoltage():
	port.write( 'VN\r' );	#Request nominal current
	time.sleep(1);
	#answerVN = "*0000032000";
	answerVN = port.readline(12);
	answerVN = answerVN[1:];	#Delete * in the front of the answer
	return answerVN;

def actualVoltage():
	time.sleep(3);
	port.write( 'VA\r' );	#Request actual current
	time.sleep(1);
	#answerVA = "*0000032000";
	answerVA = port.readline(12);
	answerVA = answerVA[1:];
	return answerVA;
	

#shutter 2: back
#shutter 3: down

def openShutter(int_shutternumber):
	while(int_shutternumber != 2 and int_shutternumber != 3 or type(int_shutternumber) != int):
		int_shutternumber = input("Please choose a correct shutternumber to open (2 (back) or 3 (down)... ");
	string = 'OS:%01d\r' % int_shutternumber;	#Produce right formatted command
	#print string;
	port.write( string );
	time.sleep(3);
	if(int_shutternumber == 2):
		return statusRead3();
	if(int_shutternumber == 3):
		return statusRead4();

def closeShutter(int_shutternumber):
	while(int_shutternumber != 2 and int_shutternumber != 3 or type(int_shutternumber) != int):
		int_shutternumber = input("Please choose a correct shutternumber to close (2 (back) or 3 (down)... ");
	string = 'CS:%01d\r' % int_shutternumber;	#Produce right formatted command
	#print string;
	port.write( string );
	time.sleep(3);
	if(int_shutternumber == 2):
		return(not statusRead3());
	if(int_shutternumber == 3):
		return(not statusRead4());

def statusRead3():	#status window 1 and 2
	string = 'SR:03\r';	
	port.write( string );
	time.sleep(1);
	#answerSR3 = "*0000000064\r";
	answerSR3 = port.readline(12);
	answerSR3 = answerSR3[1:];					#delete * at the beginning
	answerSR3 = answerSR3[:len(answerSR3)-1];	#delete CR at the end
	#print "Statuswort 3 vor Ueberpruefung ", int(answerSR3);
	if(int(answerSR3) != 16 and int(answerSR3) != 28):
		print "Unexpected status word (concerning shutter 2)"
		print "WARNING: you have to check which settings are shown on display of tube before opening the doors!!!"
		print "Maybe the doors aren't closed in the right way."
		print "Program will now end"
		print "WARNING: you have to check which settings are shown on display of tube before opening the doors!!!"
		sys.exit()
		return(-1);
	else:
		binary = bin(int(answerSR3));
		binary = binary[2:].zfill(8);				#delete 0b at the beginning and fill with zeros
	
		print "Status shutter 2 (back):"
		if(int(binary[7-2]) == 1):
			print "shutter 2 is open!";
			return True;
		if(int(binary[7-1]) == 1):
			print "shutter 2 is closed, please check if door is closed!"
			return False;
		else:
			print "shutter 2 is closed!";
			return False;

def statusRead4():	#status window 3 and 4
	string = 'SR:04\r';	
	port.write( string );
	time.sleep(1);
	#answerSR4 = "*0000000064";
	answerSR4 = port.readline(12);
	answerSR4 = answerSR4[1:];
	answerSR4 = answerSR4[:len(answerSR4)-1];
	binary = bin(int(answerSR4));
	binary = binary[2:].zfill(8);			#delete 0b at the beginning of the binary string and fill with zeros
	#print answerSR4
	if(int(answerSR4) != 5 and int(answerSR4) != 197):
		print "Unexpected status word (concerning shutter 3)"
		print "WARNING: you have to check which settings are shown on display of tube before opening the doors!!!"
		print "Maybe the doors aren't closed in the right way."
		print "Program will now end"
		print "WARNING: you have to check which settings are shown on display of tube before opening the doors!!!"
		sys.exit()
		return(-1)
	else:
		print "Status shutter 3 (down): "
		if(int(binary[7-6]) == 1):
			print "shutter 3 is open!";
			return True;
		if(int(binary[7-5]) == 1):
			print "shutter 3 is closed, please check if door is closed!"
			return False;
		else:
			print "shutter 3 is closed!";
			return False;		


def actSettings():
	print "The actual settings and parameters of the tube are"
	nomcurrent = 0.001*float(nominalCurrent());
	actcurrent = 0.001*float(actualCurrent());
	nomvoltage = 0.001*float(nominalVoltage());
	actvoltage = 0.001*float(actualVoltage());
	print "            \tnominal\t\tactual"
	print "Voltage (kV)\t ", nomvoltage, "\t\t ", actvoltage;
	print "Current (mA)\t ", nomcurrent, "\t\t ", actcurrent;
	statusRead3();
	statusRead4();



def runXraytest(pXardir, datadirectory, ac, runnr, trimVcal):
	runnrAct = '%03d' % runnr;
	rootfile = 'Spectrum_{0}_{1}mA-run{2}.root'.format(target, ac, runnrAct)
	destination = '{0}'.format(datadirectory)
	maindir = '{0}/{1}'.format(pXardir,'main')
	#print destination;
	print "cat %s/xraytest | .%s/bin/pXar -d %s -T %i -r %s" % (maindir,pXardir,destination,trimVcal, rootfile)
	os.system("cat %s/xraytest | %s/bin/pXar -d %s -T %i -r %s" % (maindir,pXardir,destination,trimVcal, rootfile))

#--------------------------------------------------------------------------------------------------------------------------------------

#Output in .log file and on shell
class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)

title = '{0}/Spectrum_{1}_{2}-{3}mA.log'.format(datadirectory, target, desCurrentBegin, desCurrentEnd);
print "Log file: ", title;
f = open(title, 'w')
original = sys.stdout
sys.stdout = Tee(sys.stdout, f)

print strftime("%Y-%m-%d %H:%M:%S", gmtime());		#start time

print "This program will measure spectra at different current values of the X-ray tube\n";

if not os.path.exists(datadirectory):
	print "False data directory, path doesn't exist";
	sys.exit();
maindir = '{0}/{1}'.format(pXardir,'main')		#Directory to start pXar
os.system("sed -i.backup -e 's/source.*/source              '%s'/'  %s/testParameters.dat" % (target, datadirectory))	#change source in testParameters.dat and backup the file


port = serial.Serial('/dev/ttyS0')
#Syntax: serial.Serial(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, writeTimeout=None, dsrdtr=False, interCharTimeout=None)
#Timeout setzen?

actSettings();	#print the actual settings

UserPleased = 0;
while(UserPleased != 1):
	#Test if values of variables are ok
	if(testVoltage(desVoltage == False)):
		print "False setting at desVoltage";
		sys.exit();
	if(testCurrent(desCurrentBegin == False)):
		print "False setting at desCurrentBegin";
		sys.exit();
	if(testCurrent(desCurrentEnd == False)):
		print "False setting at desCurrentEnd";
		sys.exit();
	if(desCurrentStep < 1 or desCurrentStep > (desCurrentEnd-desCurrentBegin) or type(desCurrentStep) != int):
		print "False setting at desCurrentStep";
		sys.exit();
	
	listCurrent = range(desCurrentBegin, desCurrentEnd+1, desCurrentStep);	#List of current steps at which data will be measured
	print "*************************************************************"
	print "*Please control the settings before starting the measurement*"
	print "Temperature\t", temperature;
	print "TrimVcal\t", trimVcal;
	print "RunNr Begin\t", runnrBegin;
	print "Target\t", target;
	print "Voltage\t", desVoltage;
	print "Currents\t", listCurrent;	
	print "*************************************************************"
	
	UserPleased = input("Is this what you wished? (Yes = 1, No = 0) ");
	if(UserPleased != 1):
		print "Ok, then please change the settings in the program code. Program will end here. Bye ...";
		sys.exit();

#**************************************************************************************************************************
#Start of the measurement
minutes = len(listCurrent)*4;
print "Angenommene Messzeit: %i min" % (minutes);

setVoltage(desVoltage);

#listCurrent = [2,6,10,30]

counter = 0;
for ac in listCurrent:
	setCurrent(ac);
	actSettings();
	openShutter(3);
	time.sleep(15);		#Wait to get a stable radiation
	runnr = runnrBegin+counter;
	counter = counter + 1;
	runXraytest(pXardir, datadirectory, ac, runnr, trimVcal)
	closeShutter(3);
	print "###############################################################################################################"

setCurrent(2);
setVoltage(40);
actSettings();
closeShutter(3);
closeShutter(2);

#logbackup = '{0}.backup'.format(title);
#os.remove(logbackup);
print '{0}/testParameters.dat'.format(datadirectory)
os.remove('{0}/testParameters.dat'.format(datadirectory))
os.rename('{0}/testParameters.dat.backup'.format(datadirectory), '{0}/testParameters.dat'.format(datadirectory))

print strftime("%Y-%m-%d %H:%M:%S", gmtime());	#ending time
