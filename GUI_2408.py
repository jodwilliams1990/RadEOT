from Tkinter import *
import os
import time 
import sys
import subprocess
import signal
import tkFont as font
from PIL import ImageTk, Image


#Home window, small or large antenna 
class Buttons:

        def __init__(self, master):
                self.master = master
                self.frame = Frame(self.master)
                #Quit, radio and H button generation and format
                Font = font.Font(weight='bold')
                self.b1 = Button(self.master, text="Listen to FM Radio", height = 3, width = 20, command = self.new_window1, bg='blue') 
                self.b2 = Button(self.master, text="Detect Hydrogen Lines", height = 3, width = 20, command=self.new_window2,bg='blue') 
                self.b3 = Button(self.master, text="Track Aeroplanes", height = 3, width = 20, command=self.new_window3,bg='blue')
                self.b4 = Button(self.master, text="Decode Radio signals", height = 3, width = 20, command=self.new_window4,bg='blue')
                self.quit = Button(root, text="Quit", command=root.destroy, height = 3, width = 10, bg='red')
                self.quit.place(relx=0.5, rely=0.6, anchor=CENTER)
                self.b1.place(relx=0.4, rely=0.2, anchor=CENTER)
                self.b2.place(relx=0.6, rely=0.2, anchor=CENTER)
                self.b3.place(relx=0.4, rely=0.4, anchor=CENTER)
                self.b4.place(relx=0.6, rely=0.4, anchor=CENTER)

                label_home = Label(master, text = "What activity would you like to do?")
                label_home.place(relx = 0.5, rely = 0.05, anchor = CENTER)

                #Insert pictures at the side, just placeholders for now, actual desgin to come later
                '''image = Image.open("test.jpg")
                photo = ImageTk.PhotoImage(image)
                label = Label(image=photo)
                label.image_r = photo
                label.place(relx = 0.2, rely = 0.6, anchor = CENTER)

                image = Image.open("hydrogen.jpg")
                photo = ImageTk.PhotoImage(image)
                label = Label(image=photo)
                label.image = photo 
                label.place(relx = 0.8, rely = 0.6, anchor = CENTER)'''

        #open radio tune window 
        def new_window1(self):
                self.master.withdraw()
                self.newWindow1 = Toplevel(self.master)
                nw1 = Radio(self.newWindow1)
                self.newWindow1.geometry('%dx%d+0+0' % (width,height))
                self.newWindow1.title('FM Radio')

        #open H info window
        def new_window2(self):
                self.master.withdraw()
                self.newWindow2= Toplevel(self.master)
                nw2 = Hydrogen(self.newWindow2)
                self.newWindow2.geometry('%dx%d+0+0' % (width,height))
                self.newWindow2.title('Hydrogen')

        def new_window3(self):
                self.master.withdraw()
                self.newWindow3= Toplevel(self.master)
                nw3 = Planes(self.newWindow3)
                self.newWindow3.geometry('%dx%d+0+0' % (width,height))
                self.newWindow3.title('Planes')

        def new_window4(self):
                self.master.withdraw()
                self.newWindow4= Toplevel(self.master)
                nw4 = Decode(self.newWindow4)
                self.newWindow4.geometry('%dx%d+0+0' % (width,height))
                self.newWindow4.title('Decode')


#If FM Radio chosen follow this path
class Radio():

        def __init__(self, master):
                self.master = master
                self.frame = Frame(self.master)
                self.r1 = Button(self.master, text="Yes", command=self.radio_yes, height = 3, width = 10, bg = 'blue')
                self.r2 = Button(self.master, text="No", command=self.radio_no, height = 3, width = 10, bg='blue')
                self.quit3 = Button(self.master, text="Quit", command = self.frame.quit, height = 3, width = 10, bg='red')

                self.quit3.place(relx=0.5, rely=0.4, anchor=CENTER)
                self.r1.place(relx=0.4, rely=0.2, anchor=CENTER)
                self.r2.place(relx=0.6, rely=0.2, anchor=CENTER)

                label_tune = Label(master, text = "Would you like to tune the radio yourself?")
                label_tune.place(relx = 0.5, rely = 0.05, anchor = CENTER)

        #leave the gui and open other software
        def radio_yes(self):
                os.chdir('/usr/local/bin')
                os.system('gqrx')#./gqrx; ./gqrx')
                os.chdir('/home/pi/Documents/scripts')

        #open new window to pick radio station
        def radio_no(self):
                self.master.withdraw()
                self.newWindow3= Toplevel(self.master)
                nw3 = Tune(self.newWindow3)             
                self.newWindow3.geometry('%dx%d+0+0' % (width,height))
                self.newWindow3.title('FM Radio')


#If want auto tune follow this so can pick choice of 2 radio stations
#This could be adapted to just have space to enter fm frequency and play straight from gui
class Tune():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.fm1 = Button(self.master, text="National Radio", command=self.fm1, height = 3, width = 10, bg='blue')
                self.fm2 = Button(self.master, text="Local Radio", command=self.fm2,height = 3, width = 10, bg = 'blue')
                self.quit1 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')

                self.quit1.place(relx=0.5, rely=0.5, anchor=CENTER)
                self.fm1.place(relx=0.4, rely=0.3, anchor=CENTER)
                self.fm2.place(relx=0.6, rely=0.3, anchor=CENTER)

                label_station = Label(master, text = "Which Radio Station would you like to listen to?")
                label_station.place(relx = 0.5, rely = 0.2, anchor = CENTER)

                label_time = Label(master, text = "How long do you want to listen for? (in seconds)")
                label_time.place(relx = 0.5, rely = 0.05, anchor = CENTER)

                self.entry = Entry(self.master)
                self.entry.place(relx=0.5, rely=0.1, anchor=CENTER)

                #KEYPAD buttons
                self.number1 = Button(self.master, text = "1", command = self.num1)
                self.number1.place(relx = 0.15,rely=0.1,anchor=CENTER)

                self.number2 = Button(self.master, text = "2", command = self.num2)
                self.number2.place(relx = 0.2,rely=0.1,anchor=CENTER)

                self.number3 = Button(self.master, text = "3", command = self.num3)
                self.number3.place(relx = 0.25,rely=0.1,anchor=CENTER)

                self.number4 = Button(self.master, text = "4", command = self.num4)
                self.number4.place(relx = 0.15,rely=0.2,anchor=CENTER)

                self.number5 = Button(self.master, text = "5", command = self.num5)
                self.number5.place(relx = 0.2,rely=0.2,anchor=CENTER)

                self.number6 = Button(self.master, text = "6", command = self.num6)
                self.number6.place(relx = 0.25,rely=0.2,anchor=CENTER)

                self.number7 = Button(self.master, text = "7", command = self.num7)
                self.number7.place(relx = 0.15,rely=0.3,anchor=CENTER)

                self.number8 = Button(self.master, text = "8", command = self.num8)
                self.number8.place(relx = 0.2,rely=0.3,anchor=CENTER)

                self.number9 = Button(self.master, text = "9", command = self.num9)
                self.number9.place(relx = 0.25,rely=0.3,anchor=CENTER)

                self.number0 = Button(self.master, text = "0", command = self.num0)
                self.number0.place(relx = 0.15,rely=0.4,anchor=CENTER)

                self.numberB = Button(self.master, text = "Clear", command = self.numB)
                self.numberB.place(relx = 0.22,rely=0.4,anchor=CENTER)

        #Functions to put number in the entry box
        def num1(self):
                self.entry.insert(0,"1")

        def num2(self):
                self.entry.insert(0,"2")

        def num3(self):
                self.entry.insert(0,"3")

        def num4(self):
                self.entry.insert(0,"4")

        def num5(self):
                self.entry.insert(0,"5")

        def num6(self):
                self.entry.insert(0,"6")

        def num7(self):
                self.entry.insert(0,"7")

        def num8(self):
                self.entry.insert(0,"8")

        def num9(self):
                self.entry.insert(0,"9")

        def num0(self):
                self.entry.insert(0,"0")

        def numB(self):
                self.entry.delete(0,END)


        #fn for national station, stops after secs entered by user
        def fm1(self):
                print 'BBC Radio 1'
                timer = self.entry.get()
                os.chdir('/usr/local/bin/rtlfm')
                os.system('rtl_fm -M wbfm -f 97.9M | play -r 32k -t raw -e s -b 16 -c 1 -V1 - &')
                os.chdir('/home/pi/Documents/scripts')

                radio_stop = 'sleep ' + str(timer) + '; pkill rtl_fm'
                print radio_stop                
                os.system(radio_stop)

        #fn for a local station, stops after secs entered by user
        def fm2(self):
                print 'BBC Radio Leicester'
                timer = self.entry.get()
                os.chdir('/usr/local/bin')
                os.system('rtl_fm -M wbfm -f 104.9M | play -r 32k -t raw -e s -b 16 -c 1 -V1 - &')
                radio_stop = 'sleep ' + str(timer) + '; pkill rtl_fm'
                os.system(radio_stop)
                os.chdir('/home/pi/Documents/scripts')


#If H is chosen 
class Hydrogen():

        #Have a window with text and info on about how to use and what it detects etc...
        def __init__(self, master):
                self.master = master
                self.frame = Frame(self.master)
                self.h1 = Button(self.master, text="Next", command=self.displayH,height = 3, width = 10, bg = 'blue')
                self.quit2 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')

                self.quit2.place(relx=0.5, rely=0.4, anchor=CENTER)
                self.h1.place(relx=0.5, rely=0.2, anchor=CENTER)

                ##### NEED TO RESEARCH AND ADD SOME BULLET POINT INFO IN HERE #####

                label1 = Label(master, text="Electromagnetic radiation is released when a neutral hydrogen's electron \n flips its spin. It is rare but due to radio waves being able to penetrate dust and gas \n enough reach Earth to be able to be detected on this horn antenna")
                label1.place(relx = 0.5, rely = 0.075, anchor = CENTER)

        #after next is pressed move to data collection
        def displayH(self):
                self.master.withdraw()
                self.newWindow4= Toplevel(self.master)
                nw4 = DetectingH(self.newWindow4)
                self.newWindow4.geometry('%dx%d+0+0' % (width,height))
                self.newWindow4.title('H emission detection')


#After info about detecting hydrogen
class DetectingH():

        #Window asking student what frequency the H line will be detected at 
        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit4 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')
                self.quit4.place(relx=0.5, rely=0.6, anchor=CENTER)

                label_freq = Label(master, text = "At the speed of light, the wavelength of hydrogen emissions\nis 21cm. Using the equation velocity = frequency x wavelength,\nfind the frequency at which you should tune to.")
                label_freq.place(relx = 0.5, rely = 0.05, anchor = CENTER)

                self.entry = Entry(self.master)
                self.button1 = Button(self.master, text="Next", command=self.next, height = 3, width = 10, bg='blue')
                self.entry.place(relx=0.5, rely=0.2, anchor=CENTER)
                self.button1.place(relx=0.5, rely=0.3, anchor=CENTER)

                #Hint button included
                self.hint = Button(self.master, text = "Hint", command = self.hint, height = 3, width = 10, bg='green')
                self.hint.place(relx = 0.5, rely = 0.45, anchor=CENTER)

                #add numpad in here so can answer Q
                #KEYPAD buttons
                self.number1 = Button(self.master, text = "1", command = self.num1)
                self.number1.place(relx = 0.15,rely=0.1,anchor=CENTER)

                self.number2 = Button(self.master, text = "2", command = self.num2)
                self.number2.place(relx = 0.2,rely=0.1,anchor=CENTER)

                self.number3 = Button(self.master, text = "3", command = self.num3)
                self.number3.place(relx = 0.25,rely=0.1,anchor=CENTER)

                self.number4 = Button(self.master, text = "4", command = self.num4)
                self.number4.place(relx = 0.15,rely=0.2,anchor=CENTER)

                self.number5 = Button(self.master, text = "5", command = self.num5)
                self.number5.place(relx = 0.2,rely=0.2,anchor=CENTER)

                self.number6 = Button(self.master, text = "6", command = self.num6)
                self.number6.place(relx = 0.25,rely=0.2,anchor=CENTER)

                self.number7 = Button(self.master, text = "7", command = self.num7)
                self.number7.place(relx = 0.15,rely=0.3,anchor=CENTER)

                self.number8 = Button(self.master, text = "8", command = self.num8)
                self.number8.place(relx = 0.2,rely=0.3,anchor=CENTER)

                self.number9 = Button(self.master, text = "9", command = self.num9)
                self.number9.place(relx = 0.25,rely=0.3,anchor=CENTER)

                self.number0 = Button(self.master, text = "0", command = self.num0)
                self.number0.place(relx = 0.15,rely=0.4,anchor=CENTER)

                self.numberB = Button(self.master, text = "Clear", command = self.numB)
                self.numberB.place(relx = 0.22,rely=0.4,anchor=CENTER)

        #Functions to put number in the entry box
        def num1(self):
                self.entry.insert(0,"1")

        def num2(self):
                self.entry.insert(0,"2")

        def num3(self):
                self.entry.insert(0,"3")

        def num4(self):
                self.entry.insert(0,"4")

        def num5(self):
                self.entry.insert(0,"5")

        def num6(self):
                self.entry.insert(0,"6")

        def num7(self):
                self.entry.insert(0,"7")

        def num8(self):
                self.entry.insert(0,"8")

        def num9(self):
                self.entry.insert(0,"9")

        def num0(self):
                self.entry.insert(0,"0")

        def numB(self):
                self.entry.delete(0,END)



        def next(self):
                self.master.withdraw()
                self.newWindow5 = Toplevel(self.master)
                nw5 = ListeningH(self.newWindow5)
                self.newWindow5.geometry('%dx%d+0+0' % (width,height))
                self.newWindow5.title('H detection')

        #Hint button gives wavelength and speed of light
        def hint(self):
                self.label_hint = Label(self.master, text = "The speed of light is 300,000,000m/s\nWhat are the units for wavelength?")
                self.label_hint.place(relx = 0.5, rely = 0.75, anchor = CENTER)


#Try and find H lines
class ListeningH():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit5 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg ='red')
                self.quit5.place(relx=0.5, rely=0.4, anchor=CENTER)

                self.gqrx = Button(self.master, text="Open GQRX", command = self.open_gqrx, height = 3, width = 10, bg='blue')
                self.gqrx.place(relx=0.5, rely=0.2, anchor=CENTER)

                self.answer = Label(self.master, text = "The correct answer is 1420MHz \n Now try and pick up the signal!")
                self.answer.place(relx = 0.5, rely = 0.1, anchor = CENTER)

        #Open gqrx to detect the H radio lines
        def open_gqrx(self):
                os.chdir('/usr/local/bin')
                os.system('gqrx')#./gqrx; ./gqrx')
                os.chdir('/home/pi/Documents/scripts')
                #os.system('cd /usr/local/bin')
                #os.system('../gqrx; ./gqrx &')


#Class that can be edited or included to pick radio frequency and timer (not in use at the moment)
'''class listen():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit4 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, highlightbackground='#c63f33')
                self.quit4.place(relx=0.5, rely=0.4, anchor=CENTER)

                label_freq = Label(master, text = "What frequency do you want to tune to?")
                label_freq.place(relx = 0.5, rely = 0.1, anchor = CENTER)

                self.entry1 = Entry(self.master)
                self.button1 = Button(self.master, text="Get", command=self.on_button)
                self.entry1.place(relx=0.5, rely=0.2, anchor=CENTER)
                self.button1.place(relx=0.5, rely=0.25, anchor=CENTER)

                self.entry2 = Entry(self.master)
                self.entry2.place(relx=0.5, rely=0.3, anchor=CENTER)


        def on_button(self):
                freq = self.entry1.get()
                timer = self.entry2.get()
                radio_play = 'rtl_fm -M wbfm -f' + str(freq) + 'M | play -r 32k -t raw -e s -b 16 -c 1 -V1 - &'
                radio_stop = 'sleep ' + str(timer) + '; pkill rtl_fm'
                os.system(radio_play)
                os.system(radio_stop)'''


#detect planes flying overhead
class Planes():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit5 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')
                self.quit5.place(relx=0.5, rely=0.4, anchor=CENTER)
		self.open = Button(self.master, text="Track Aeroplanes", command = self.track, height = 3, width = 10, bg = 'blue')
		self.open.place(relx=0.5, rely=0.2,anchor=CENTER)

	def track(self):
		os.system('xdg-open http://localhost:8080 &')



#decode tutorial using gqrx, rtl_sdr and octave
class Decode():

        #breif instructions
        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit6 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')
                self.quit6.place(relx=0.5, rely=0.6, anchor=CENTER)     
                self.next = Button(self.master, text="Next", command = self.next, height = 3, width = 10, bg = 'blue')
                self.next.place(relx=0.5, rely=0.4, anchor=CENTER)                      

                self.decode_info = Label(self.master, text = "In FM Stereo Broadcasting there are a number of \n characteristic peaks in the frequency spectrum \n indicating that frequency is an FM radio station")
                self.decode_info.place(relx = 0.5, rely = 0.1, anchor = CENTER)

                self.decode_tut = Label(self.master, text = "Following this tutorial you will be able to \n tune the radio antenna to a specific frequency \n and identify the different parts of the signal")
                self.decode_tut.place(relx = 0.5, rely = 0.25, anchor = CENTER)

        #open window to next stage
        def next(self):
                self.master.withdraw()
                self.newWindow6 = Toplevel(self.master)
                nw6 = gqrx(self.newWindow6)
                self.newWindow6.geometry('%dx%d+0+0' % (width,height))
                self.newWindow6.title('GQRX')


#open gqrx
class gqrx():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit8 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')
                self.quit8.place(relx=0.5, rely=0.6, anchor=CENTER)
                self.gqrx = Button(self.master, text="Open GQRX", command = self.gqrx_open, height = 3, width = 10, bg = 'blue')
                self.gqrx.place(relx=0.5, rely=0.27, anchor=CENTER)
                self.info = Label(self.master, text = "Use the software GQRX to find an FM radio station \n and note the central frequency. \n Once you have found a frequency, close the GQRX and press next.")
                self.info.place(relx=0.5, rely=0.1, anchor=CENTER)
                self.next = Button(self.master, text="Next", command = self.next, height = 3, width = 10, bg = 'blue')
                self.next.place(relx=0.5, rely=0.43, anchor=CENTER)

        def next(self):
                self.master.withdraw()
                self.newWindow7 = Toplevel(self.master)
                nw7 = Radio_data(self.newWindow7)
                self.newWindow7.geometry('%dx%d+0+0' % (width,height))
                self.newWindow7.title('Radio')

        def gqrx_open(self):
                os.chdir('/usr/local/bin')
                os.system('gqrx')#./gqrx; ./gqrx')
                os.chdir('/home/pi/Documents/scripts')
                #os.system('gqrx &')


#user inputs freq from gqrx and then collects 1 sec of radio info
class Radio_data():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit9 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')
                self.quit9.place(relx=0.5, rely=0.65, anchor=CENTER)
                self.rtl = Button(self.master, text = "Collect Data", command = self.rad_data, height = 3, width = 10, bg = 'blue')
                self.rtl.place(relx = 0.5, rely = 0.35, anchor=CENTER)
                self.next = Button(self.master, text="Next", command = self.Octave, height = 3, width = 10, bg = 'blue')
                self.next.place(relx=0.5, rely = 0.5, anchor=CENTER)
                self.input = Label(self.master, text = "What frequency was the radio station at?")
                self.input.place(relx=0.5, rely = 0.1, anchor=CENTER)
                self.entry = Entry(self.master)
                self.entry.place(relx=0.5, rely=0.2, anchor=CENTER)


                #KEYPAD buttons
                self.number1 = Button(self.master, text = "1", command = self.num1)
                self.number1.place(relx = 0.15,rely=0.1,anchor=CENTER)

                self.number2 = Button(self.master, text = "2", command = self.num2)
                self.number2.place(relx = 0.2,rely=0.1,anchor=CENTER)

                self.number3 = Button(self.master, text = "3", command = self.num3)
                self.number3.place(relx = 0.25,rely=0.1,anchor=CENTER)

                self.number4 = Button(self.master, text = "4", command = self.num4)
                self.number4.place(relx = 0.15,rely=0.2,anchor=CENTER)

                self.number5 = Button(self.master, text = "5", command = self.num5)
                self.number5.place(relx = 0.2,rely=0.2,anchor=CENTER)

                self.number6 = Button(self.master, text = "6", command = self.num6)
                self.number6.place(relx = 0.25,rely=0.2,anchor=CENTER)

                self.number7 = Button(self.master, text = "7", command = self.num7)
                self.number7.place(relx = 0.15,rely=0.3,anchor=CENTER)

                self.number8 = Button(self.master, text = "8", command = self.num8)
                self.number8.place(relx = 0.2,rely=0.3,anchor=CENTER)

                self.number9 = Button(self.master, text = "9", command = self.num9)
                self.number9.place(relx = 0.25,rely=0.3,anchor=CENTER)

                self.number0 = Button(self.master, text = "0", command = self.num0)
                self.number0.place(relx = 0.15,rely=0.4,anchor=CENTER)

                self.numberB = Button(self.master, text = "Clear", command = self.numB)
                self.numberB.place(relx = 0.22,rely=0.4,anchor=CENTER)

        #Functions to put number in the entry box
        def num1(self):
                self.entry.insert(0,"1")

        def num2(self):
                self.entry.insert(0,"2")

        def num3(self):
                self.entry.insert(0,"3")

        def num4(self):
                self.entry.insert(0,"4")

        def num5(self):
                self.entry.insert(0,"5")

        def num6(self):
                self.entry.insert(0,"6")

        def num7(self):
                self.entry.insert(0,"7")

        def num8(self):
                self.entry.insert(0,"8")

        def num9(self):
                self.entry.insert(0,"9")

        def num0(self):
                self.entry.insert(0,"0")

        def numB(self):
                self.entry.delete(0,END)

        #use rtl_sdr to collect data
        def rad_data(self):
                freq = self.entry.get()
                data_collect = 'rtl_sdr -f ' + str(freq) + ' -g 20 -s 2500000 -n 2500000 capture.dat'
                os.system(data_collect)
                self.done = Label(self.master, text = "The data has been collected")
                self.done.place(relx = 0.5, rely = 0.5, anchor=CENTER)

        #next window
        def Octave(self):
                self.master.withdraw()
                self.newWindow8 = Toplevel(self.master)
                nw8 = Octave(self.newWindow8)
                self.newWindow8.geometry('%dx%d+0+0' % (width,height))
                self.newWindow8.title('Script')         


#open octave
class Octave():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit7 = Button(self.master, text="Quit", command = self.frame.quit,height = 3, width = 10, bg='red')
                self.quit7.place(relx=0.5, rely=0.7, anchor=CENTER)
                self.info = Label(self.master, text = "Open the script in the text editor\n Then follow the instructions until you have generated the frequency spectrum \n And press next to compare and analyse your graph.")
                self.info.place(relx=0.5, rely=0.1, anchor=CENTER)
                self.open = Button(self.master, text="Open Script", command = self.open_script, height = 3, width = 10, bg = 'blue')
                self.open.place(relx=0.5, rely = 0.25, anchor=CENTER)
                self.next = Button(self.master, text="Next", command = self.next, height = 3, width = 10, bg = 'blue')
                self.next.place(relx=0.5, rely=0.4, anchor=CENTER)
                self.run = Button(self.master, text="Run Script", command = self.run_script, height = 3, width = 10, bg = 'blue')
                self.run.place(relx=0.5, rely = 0.55, anchor=CENTER)

        #open demodulation script in separate window along with touchscreen keyboard
        def open_script(self):
                os.system('gedit demod.py &')
                #os.system('keyboard &') need to open the keyboard along so student can edit the script 
                #NEED TO ADD INSTRUCTIONS ONTO THE SCRIPT FOR THE STUDENT TO FOLLOW ALONG WITH CORRECT ANSWER

        #run the script the student has just edited - what if it doesn't run..? 
        def run_script(self):
                os.system('python demod.py')
                self.done = Label(self.master, text = "The script ran successfully")
                self.done.place(relx = 0.5, rely = 0.5, anchor=CENTER)  

        #new window to comapre figures
        def next(self):
                self.master.withdraw()
                self.newWindow8 = Toplevel(self.master)
                nw8 = compare(self.newWindow8)
                self.newWindow8.geometry('%dx%d+0+0' % (width,height))
                self.newWindow8.title('Comapre figures')


#window which opens figure just generated from octave and also comparison pic
class compare():

        def __init__(self,master):
                self.master = master
                self.frame = Frame(self.master)
                self.quit8 = Button(self.master, text="Quit", command = self.frame.quit, height = 3, width = 10, bg='red')
                self.quit8.place(relx=0.5, rely=0.6, anchor=CENTER)

#WHY DONT THESE PHOTOS SHOW UP??? 
                photo2 = PhotoImage("FM_spectrum.png")
                label = Label(image=photo2)
                label.image = photo2
                label.place(relx = 0.5, rely = 0.8, anchor = CENTER)

                photo3 = PhotoImage("plot_.png")
                label = Label(image=photo3)
                label.image = photo3
                label.place(relx = 0.5, rely = 0.8, anchor = CENTER)

#main function to start GUI
if __name__ == '__main__':
        root = Tk()
        b = Buttons(root)

        width, height = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry('%dx%d+0+0' % (width,height))
        #root.configure(background='black')
        root.title('Home')
        root.mainloop()

