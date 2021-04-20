from time import sleep
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD
import paho.mqtt.client as mqtt

BOARD.setup() #setup raspberry pi pins



class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):  #initialisation of LoRa receiver
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def on_rx_done(self): #when the packet is received
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True) #read incoming data and save them to "payload"
        flame=bytes(payload); 
        client.publish("metrics/exchangemut0022",flame); #MQTT - when packet is received, send data 
        
        
        print("Flame: ")
        print(bytes(payload).decode("utf-8",'ignore'))
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx() #reset module and be ready for another incoming packet
        self.set_mode(MODE.RXCONT)

    def start(self): #when receiver starts
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT) #set mode to RX
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value() #get signal strength value
            status = self.get_modem_status() #get overall status of the receiver
            sys.stdout.flush()
            sys.stdout.write("\rRSSI: %d " % (rssi_value)) #print the signal strength value


lora = LoRaRcvCont(verbose=False) 
lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1) #set default parameters for receiver (169 MHz, 125kHz band,...)
print(lora) #print all the parameters

client = mqtt.Client("mut0022client-2512"); #create MQTT client
client.connect("broker.emqx.io",1883); #connect to online broker

#start LoRa receiver
try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()  
