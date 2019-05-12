'''
from kivy.lib import osc
from random import sample, randint
from string import ascii_letters
from time import localtime, asctime, sleep


def ping(*args):
    osc.sendMsg(
        '/message',
        [''.join(sample(ascii_letters, randint(10, 20))), ],
        port=3002)


def send_date():
    osc.sendMsg('/date', [asctime(localtime()), ], port=3002)


if __name__ == '__main__':
    osc.init()
    oscid = osc.listen(ipAddr='0.0.0.0', port=3000)
    osc.bind(oscid, ping, '/ping')
    while True:
        osc.readQueue(oscid)
        send_date()
        sleep(.1)
'''

import os, sys

devslibpath = os.path.join("..", "devslib")
print("DEVSLIBPATH: ", devslibpath)
sys.path.append( devslibpath )

#kivy stuff
from kivy.core.audio import SoundLoader

from time import sleep
from network import Network

def receiver(data, addr):

    data_dict = json.loads(data)

    if data_dict['msg'] == 'ping_ack':        
        print('PING ACK RECEIVED FROM ', addr, data_dict['data'])
        
        #self.machines[data_dict['data']] = addr[0]
        #self.spn_machine.text = data_dict['data']
        #self.spn_machine.values.append(data_dict['data'])


if __name__ == '__main__':

    #start network stuff (UDP netget networking)
    net = Network()  
    net.create_connection(receiver)
    #net.host_discover()

    '''
    #start test sound
    sound = SoundLoader.load("abucheo.mp3")
    
    if sound:
        print("Sound found at %s" % sound.source)
        print("Sound is %.3f seconds" % sound.length)
        sound.play()

        #sound.bind(on_stop=app.root.on_endmedia)
    '''

    while True:
        sleep(.1)
        #print "BREAKBREAKBREKABREKABEKAZB"
