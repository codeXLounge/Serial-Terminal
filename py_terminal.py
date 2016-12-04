#!/usr/bin/env python

import serial
import pygtk
pygtk.require('2.0')
import gtk
import threading
import gobject
import csv

class GUI:

    baud_rates = ("2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", )
    port = ("/dev/ttyUSB0", "/dev/ttyS0","/dev/ttyUSB5")
    flag_serial = 0
    flag_window_focus = 0
    oldX = 0
    oldY = 0
    newX = 0
    flag_plot = 0
   
    def initSerial(self):
        port_active = self.port[self.combobox_port.get_active()]
        baud_active = self.baud_rates[self.combobox_baud.get_active()]
        self.ser = serial.Serial(port_active, baud_active, timeout = 0.001, bytesize = serial.EIGHTBITS)# write_Timeout = 0)
        self.combobox_baud.set_sensitive(False)
        self.combobox_port.set_sensitive(False)
        self.entry_usart.set_sensitive(True)
        self.entry_usart.grab_focus()
        self.entry_usart.set_text("")
        
    def closeSerial(self):
        self.ser.close()
        self.combobox_baud.set_sensitive(True)
        self.combobox_port.set_sensitive(True)
        self.entry_usart.set_sensitive(False)
        #self.flag_window_focus =0
        
    def readSerial(self):
        self.serialdata = self.ser.readline()#size = None, eol = '\n')
        #print self.serialdata
        self.enditer = self.textbuffer.get_end_iter()
        self.textbuffer.insert(self.enditer, self.serialdata)
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(),0.0)
        if self.flag_plot == 1 :
            self.draw_line(int(self.serialdata[3:5],16))
            #print int(self.serialdata[3:5],16)
        #print self.ser.inWaiting()
        #self.buffer_char_count = self.textbuffer.get_char_count()

    def transmitUSART(self, widget, data=None):
        #print "Transmit"
        self.text = widget.get_text()
        print self.ser.write(self.text[len(self.text)-1])
            
    def display(self):
       # print "display"
        if self.flag_serial == 1 and self.ser.inWaiting() != 0:
            self.readSerial()
        #elif self.flag_serial == 1 and self.ser.inWaiting() == 0:
            #self.writeSerial()
        return True       
        
	
    def connect(self, widget, data=None):
        
        if self.flag_serial == 0:
            self.flag_serial = 1
            self.initSerial()
            widget.set_label("Disconnect")
            #print "Opened"
            self.flag_window_focus =1
                                 
        elif self.flag_serial == 1:
            self.flag_serial = 0
            self.closeSerial() 
            widget.set_label("Connect")
            #print "closed"
            self.flag_window_focus = 0
            
    def clear_text(self, widget, data=None):
        #print "clear"
        self.textbuffer.set_text("")
                
    def infocus(self, widget, data=None):
		if self.flag_window_focus == 1:
		    self.initSerial()
		    self.flag_serial = 1
            
    def notinfocus(self, widget, data= None):
        self.closeSerial()
        self.flag_serial = 0
        #self.flag_window_focus = 0
            
    def delete_event(self, widget, event, data=None):
        #print "delete event occurred"
        return False

    def destroy(self, widget, data=None):
        #print "destroy signal occurred"
        if self.flag_serial == 1:
            self.closeSerial()
        gtk.main_quit()
        
    def plotTemp(self, widget, data = None):
        print "Plotting"
        self.button_plottemp.set_sensitive(False)
        self.flag_plot = 1
        
    def plotClear(self, widget, data = None):
        print "Clear Plot"
        self.button_plottemp.set_sensitive(True)
        self.flag_plot = 0
        
    def area_expose_cb(self, area, event):
        self.style = self.area.get_style()
        self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        #self.draw_line(0,0,100,100)
        
    def draw_line(self, newY):
        self.area.window.draw_line(self.gc, self.oldX, self.oldY, self.newX, newY)
        self.oldX = self.newX
        self.newX = self.newX + 1
        self.oldY = newY
        #self.pangolayout.set_text("Line")
        #self.area.window.draw_layout(self.gc, x+5, y+50, self.pangolayout)
        return
        
    def __init__(self):
        
        # Init WIndow
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_default_size (800, 500)
        self.window.set_resizable(True)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        
        # Focus Check
        self.window.set_events(gtk.gdk.FOCUS_CHANGE_MASK)
        self.window.connect("focus_in_event", self.infocus)
        self.window.connect("focus_out_event", self.notinfocus)
        self.window.set_border_width(10)
        self.window.set_title("Sost-Sat Data Logger")
    
        # Init Quit Button
        self.button_quit = gtk.Button("Quit")
        self.button_quit.connect_object("clicked", gtk.Widget.destroy, self.window)
        
        self.button_view = gtk.Button("Connect")
        self.button_view.connect("clicked", self.connect, None)
        
        self.button_clear = gtk.Button("Clear")
        self.button_clear.connect("clicked", self.clear_text, None)
        
        # Init Text View        
    	self.textview =  gtk.TextView()
    	self.textview.set_editable(True)
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_overwrite(False)
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
                
        # Init ScrollWindow      
        self.scrolledwindow =  gtk.ScrolledWindow(hadjustment = None, vadjustment = None)
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    	self.scrolledwindow.add(self.textview)

        
        # Init Label
        self.label_baud = gtk.Label("Baud Rate : ")
        self.label_port = gtk.Label("Port : ")
        self.label_input = gtk.Label("Input : ")
        self.label_about = gtk.Label(" Nano-Sat Serial Data Logger\n \n Version :7.1.0 \n Designed @ SOST Lab \n Designed By Priyashraba Misra\n International Instiute of Information Technology\n Pune ")
        self.label_about.set_justify(gtk.JUSTIFY_CENTER)
        
        # Combo for Baud, Port
        self.combobox_baud = gtk.combo_box_new_text()
        for i in self.baud_rates:
            self.combobox_baud.append_text(i)
        self.combobox_baud.set_active(0)
        
        self.combobox_port = gtk.combo_box_new_text()
        for i in self.port:
            self.combobox_port.append_text(i)
        self.combobox_port.set_active(1)
        
        #Text entru for USART write
    	self.entry_usart = gtk.Entry(max = 0)
    	self.entry_usart.connect("changed", self.transmitUSART)
        self.entry_usart.set_sensitive(False)
    	
        #HBox for Text
    	self.hbox1 = gtk.HBox (False, 0);
    	self.hbox1.pack_start(self.scrolledwindow, expand = True, fill = True, padding = 0)
    	
    	#HBox for Text
    	self.hbox2 = gtk.HBox (False, 0);
    	self.hbox2.pack_start(self.label_input, expand = False, fill = False, padding = 0)
    	self.hbox2.pack_start(self.entry_usart, expand = True, fill = True, padding = 0)
    	
        #HBox for Menus
    	self.hbox3 = gtk.HBox (False, 0);
        self.hbox3.pack_start(self.label_baud, expand = False, fill = False, padding = 0)
       	self.hbox3.pack_start(self.combobox_baud, expand = True, fill = False, padding = 0)
        self.hbox3.pack_start(self.label_port, expand = False, fill = False, padding = 5)
       	self.hbox3.pack_start(self.combobox_port, expand = True, fill = False, padding = 5)
    	self.hbox3.pack_start(self.button_view, expand = True, fill = False, padding = 5)
    	self.hbox3.pack_start(self.button_clear, expand = True, fill = False, padding = 5)
    	self.hbox3.pack_start(self.button_quit, expand = True, fill = False, padding = 5)
        
        #Vbox for stacking HBox(s)
    	self.vbox1 = gtk.VBox (False, 10);
    	self.vbox1.pack_start(self.hbox1, expand = True, fill = True, padding = 5)
    	self.vbox1.pack_start(self.hbox2, expand = False, fill = False, padding = 5)
        self.vbox1.pack_start(self.hbox3, expand = False, fill = False, padding = 5)

        #Drawing area for graph
        self.area =  gtk.DrawingArea()
        self.area.set_size_request(600,300)
        self.area.connect("expose-event", self.area_expose_cb)
        #self.area_expose_cb(self.area)
        self.area.show()
        
        #button for drawing area
        self.button_plottemp = gtk.Button("Start Plot")
        self.button_plottemp.connect("clicked", self.plotTemp, None)
        
        self.button_plotclear = gtk.Button("Clear Plot")
        self.button_plotclear.connect("clicked", self.plotClear, None)
        
        #hbox and vbox for drawing area
        self.hbox4 = gtk.HBox()
        self.hbox4.pack_start(self.area, expand = False, fill = False, padding = 5)
        
        self.hbox5 = gtk.HBox()
        self.hbox5.pack_start(self.button_plottemp, expand = False, fill = False, padding = 5)
        self.hbox5.pack_start(self.button_plotclear, expand = False, fill = False, padding = 5)
        
        self.vbox2 = gtk.VBox()
    	self.vbox2.pack_start(self.hbox4, expand = True, fill = True, padding = 5)
    	self.vbox2.pack_start(self.hbox5, expand = True, fill = True, padding = 5)    	
                        
        # Notebook for Tabs
        self.label_notepage1 = gtk.Label("Terminal")
        self.label_notepage2 = gtk.Label("Plot")
        self.label_notepage3 = gtk.Label("About")
        self.notebook =  gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.append_page(self.vbox1, self.label_notepage1)
        self.notebook.append_page(self.vbox2, self.label_notepage2)
        self.notebook.append_page(self.label_about, self.label_notepage3)
        self.notebook.show()
        
        # add to window
        self.window.add(self.notebook)
        
        # add accelerators
        self.accel_group = gtk.AccelGroup()
        self.window.add_accel_group(self.accel_group)
        self.button_view.add_accelerator("clicked", self.accel_group, ord('c'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        self.button_quit.add_accelerator("clicked", self.accel_group, ord('x'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)   
        
        #show all
    	self.button_view.show()
    	self.button_quit.show() 
    	self.button_clear.show() 
    	self.button_plottemp.show()
    	self.button_plotclear.show() 
    	self.scrolledwindow.show()	
    	self.textview.show()
        self.hbox1.show()
    	self.hbox2.show()
    	self.hbox3.show()
    	self.hbox4.show()
    	self.hbox5.show()
    	self.vbox1.show()
    	self.vbox2.show()
    	self.window.show()
        self.label_baud.show()
        self.label_port.show()
        self.label_input.show()
        self.label_about.show()
        self.label_notepage1.show()
        self.label_notepage2.show()
        self.label_notepage3.show()
        self.combobox_baud.show()
        self.combobox_port.show()
        self.entry_usart.show()
        
        # Init Timeout
        #timer = gobject.timeout_add(100,self.display)
        idle1 = gobject.idle_add(self.display)
        
        #GC
        #self.style = self.area.get_style()
        #self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
        
    def main(self):
        gtk.main()
        return 0
       
if __name__ == "__main__":
    hello = GUI()
    hello.main()
