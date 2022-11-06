import time
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.theming import ThemeManager
from kivymd.uix.picker import MDThemePicker
from kivy.uix.widget import Widget
from kivy.metrics import dp, sp
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score
import requests
from kivy.clock import Clock
from twilio.rest import Client
from time import sleep
from serial import Serial

x = 0
a = 77.66460022508264
b = 12.861451490928184
screen_helper = """
ScreenManager:
    HomeScreen:
    StartScreen:
    BufferScreen:
    BufferScreen1:
    EndScreen:

<HomeScreen>:
    name: 'home'

    Image:
        source: "D:/Hackathons/Ingenius/accident2.png"
        size_hint: None, None
        pos: self.pos
        size: root.size
        keep_ratio: False
        
    MDLabel:
        text: "SALUS"
        halign: "center"
        pos_hint: {'center_x':0.5,'center_y':0.8}

    MDRoundFlatButton:
        text: 'Next'
        pos_hint: {'center_x':0.5,'center_y':0.2}
        on_press: 
            root.manager.current = 'start'



<StartScreen>:
    name: 'start'
    
    Image:
        source: "D:/Hackathons/Ingenius/car.png"
        size_hint: None, None
        pos: self.pos
        pos_hint: {'center_x':0.2,'center_y':0.5}
        size: root.size
        keep_ratio: False
        #allow_stretch: True
    
    
    MDLabel:
        text: "Click start when you begin your ride."
        halign: "center"
        pos_hint: {'center_x':0.7,'center_y':0.6}


    MDRoundFlatButton:
        text: 'Start'
        pos_hint: {'center_x':0.7,'center_y':0.5}
        on_press:
            root.read()
            
            
<BufferScreen>:
    name: 'buffer'
    
    Image:
        source: "D:/accident3.png"
        size_hint: None, None
        pos: self.pos
        #pos_hint: {'center_x':0.2,'center_y':0.5}
        size: root.size
        keep_ratio: False
        #allow_stretch: True
    
    
    MDLabel:
        text: "We have detected a severe accident. You have a buffer period of 30 seconds to turn this off."
        halign: "center"
        pos_hint: {'center_x':0.5,'center_y':0.9}
            
    MDRoundFlatButton:
        text: 'Click here if you want to continue ride'
        pos_hint: {'center_x':0.5,'center_y':0.1}
        
        on_press:
            root.pr()

<BufferScreen1>:
    name: 'buffermod'
    
    Image:
        source: "D:/accident3.png"
        size_hint: None, None
        pos: self.pos
        #pos_hint: {'center_x':0.2,'center_y':0.5}
        size: root.size
        keep_ratio: False
        #allow_stretch: True
    
    
    MDLabel:
        text: "We have detected a possible accident. You have a buffer period of 45 seconds to turn this off."
        halign: "center"
        pos_hint: {'center_x':0.5,'center_y':0.9}
            
    MDRoundFlatButton:
        text: 'Click here to confirm you are safe'
        pos_hint: {'center_x':0.5,'center_y':0.1}
        
        on_press:
            root.pr()
              
    
<EndScreen>:
    name : 'end'


    Image:
        source: "D:/accident4.png"
        size_hint: None, None
        pos: self.pos
        #pos_hint: {'center_x':0.2,'center_y':0.5}
        size: root.size
        keep_ratio: False
        #allow_stretch: True
    
    MDLabel:
        text: 'It was a safe ride! Have a good time.'
        halign: 'center'
        pos_hint: {'center_x':0.5,'center_y':0.9}


    MDRoundFlatButton:
        text: 'Back home'
        pos_hint: {'center_x':0.5,'center_y':0.2}
        on_press: root.manager.current = 'home'   
"""


class HomeScreen(Screen):
    pass


class Buffer(Screen):
    def prep(self):
        self.manager.current="emergency"


class StartScreen(Screen):
    def read(self):
        dataset = pd.read_csv('crashData.csv')
        X = dataset.iloc[:, :-1].values
        y = dataset.iloc[:, -1].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=0)
        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test)
        classifier = SVC(kernel='rbf', random_state=0,gamma=10)
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)
        # print(np.concatenate((y_pred.reshape(len(y_pred), 1), y_test.reshape(len(y_test), 1)), 1))
        cm = confusion_matrix(y_test, y_pred)
        # print(cm)
        print(accuracy_score(y_test, y_pred))
        # make sure the 'COM#' is set according the Windows Device Manager
        arduino_port = "COM4"  # serial port of Arduino
        baud = 9600  # arduino uno runs at 9600 bauds
        fileName = "test.csv"  # name of the CSV file generated
        ser = Serial(arduino_port, baud)
        print("Connected to Arduino port:" + arduino_port)
        file1 = open(fileName, "w")
        print("Created file")
        # display the data to the terminal
        getData = str(ser.readline())
        data = getData[2:][:-5]
        print(data)

        # add the data to the file
        file = open(fileName, "a")  # append the data to the file
        file.write(data + "\n")  # write data with a newline

        # close out the file
        file.close()
        samples = 10  # how many samples to collect
        print_labels = False
        line = 0  # start at 0 because our header is 0 (not real data)
        while line <= samples:
            # incoming = ser.read(9999)
            # if len(incoming) > 0:
            if print_labels:
                if line == 0:
                    print("Printing Column Headers")
                else:
                    print("Line " + str(line) + ": writing...")
            getData = str(ser.readline())
            data = getData[2:][:-5]
            check = data.split(',')
            check[0]=int(check[0])
            check[1] = int(check[1])
            check[2] = int(check[2])
            print(data)

            file = open(fileName, "a")
            file.write(data + "\n")  # write data with a newline
            line = line + 1
            result = classifier.predict(sc.transform([check]))
            if result == 'Yes':
                '''r = requests.get("https://get.geojs.io/")
                print(r)
                ip_request = requests.get("https://get.geojs.io/v1/ip.json")
                ipAdd = ip_request.json()['ip']
                print(ipAdd)
                url = "https://get.geojs.io/v1/ip/geo/" + ipAdd + '.json'
                get_re = requests.get(url)
                get_data = get_re.json()
                '''
                a = 77.66460022508264
                b = 12.861451490928184
                hosp = GetNearbyHospitals(b, a)
                hosp.get_hospital_one()
                self.manager.current = "buffer"
                count = 0

                def counter():
                    Clock.schedule_once(callback_clock, 30)

                def callback_clock(dt):
                    global x
                    if x == 0:
                        ser = Serial('COM3', 9600)
                        # flush serial for unprocessed data
                        ser.flushInput()
                        while True:
                            command = "https://www.google.co.in/maps/@12.8688809,77.6650655,15z"
                            print(len(command))
                            if command:
                                command += "\r\n"
                                ser.write(command.encode())
                                print("Waiting for answer")
                                while True:
                                    answer = ser.readline()
                                    if answer:
                                        print("Answer:", answer)
                                        break
                                    sleep(0.1)
                            ser.flushInput()
                        print("Alerted the nearest hospital")

                counter()
                break
        print("Ride finished")
        file.close()


        '''
        global x
        x=0
        df = pd.read_csv("work.csv")
        df = df.round(2)
        for index, row in df.iterrows():
            print(row[3])
            if row[1] > 0.04 or row[1] < -0.04 or row[2] > 0.4 or row[2] < -0.4 or row[3] > 1.04 or row[3] < 0.096:
                r = requests.get("https://get.geojs.io/")
                print(r)
                ip_request = requests.get("https://get.geojs.io/v1/ip.json")
                ipAdd = ip_request.json()['ip']
                print(ipAdd)
                url = "https://get.geojs.io/v1/ip/geo/" + ipAdd + '.json'
                get_re = requests.get(url)
                get_data = get_re.json()
                a = get_data["longitude"]
                b = get_data['latitude']
                hosp = GetNearbyHospitals(b, a)
                hosp.get_hospital_one()
                self.manager.current = "buffer"
                count = 0

                def counter():
                    Clock.schedule_once(callback_clock,30)

                def callback_clock(dt):
                    global x
                    if x==0:
                        print("Alerted the nearest hospital")

                counter()
                break
            elif row[2] > 0.1 or row[2] < -0.1:
                r = requests.get("https://get.geojs.io/")
                print(r)
                ip_request = requests.get("https://get.geojs.io/v1/ip.json")
                ipAdd = ip_request.json()['ip']
                print(ipAdd)
                url = "https://get.geojs.io/v1/ip/geo/" + ipAdd + '.json'
                get_re = requests.get(url)
                get_data = get_re.json()
                a = get_data["longitude"]
                b = get_data['latitude']
                hosp = GetNearbyHospitals(b, a)
                hosp.get_hospital_one()
                self.manager.current = "buffermod"
                count = 0

                def counter():
                    Clock.schedule_once(callback_clock, 45)

                def callback_clock(dt):
                    global x
                    if x == 0:
                        print("Alerted the nearest hospital")

                counter()
                break

            else:
                time.sleep(0.3)
            self.manager.current = "end"

        '''


class BufferScreen(Screen):
        def pr(self):
            global x
            x=1
            self.manager.current = 'start'


class BufferScreen1(Screen):
    def pr(self):
        global x
        x = 1
        self.manager.current = 'start'


class EndScreen(Screen):
    pass


sm = ScreenManager()
sm.add_widget(HomeScreen(name='home'))
sm.add_widget(StartScreen(name='start'))
sm.add_widget(BufferScreen(name='buffer'))
sm.add_widget(BufferScreen1(name='buffermod'))
sm.add_widget(EndScreen(name='end'))


class GetNearbyHospitals(object):
    def __init__(self, lat, long):
        self.URL = "https://discover.search.hereapi.com/v1/discover"
        self.lat = lat
        self.long = long
        self.api_key = 'A7BFpRoYyX1u4_narvdwcYieNuSPMMQd5Qg-VC9Msow'
        self.query = 'hospitals'
        self.limit = 5
        self.PARAMS = {
            'apikey': self.api_key,
            'q': self.query,
            'limit': self.limit,
            'at': '{},{}'.format(self.lat, self.long)
        }

    def retrieve_places(self):
        get_r = requests.get(url=self.URL, params=self.PARAMS)
        data = get_r.json()
        return data

    def get_hospital_one(self):
        data = self.retrieve_places()
        print(data)
        hospital = data['items'][1]['title']
        hospital_address = data['items'][1]['address']['label']
        hospital_num = data['items'][1]['contacts'][0]['phone'][0]['value']
        print("Hospital 1 Details -")
        print("")
        print("Name:", hospital)
        print("Address:", hospital_address)
        print("Phone number:", hospital_num)
        print("")

    def get_hospital_two(self):
        data = self.retrieve_places()
        hospital = StringProperty()
        hospital = data['items'][1]['title']
        hospital_address = data['items'][1]['address']['label']
        print("Hospital 2 Details -")
        print("")
        print("Name:", hospital)
        print("Address:", hospital_address)
        print("")

    def get_hospital_three(self):
        data = self.retrieve_places()
        hospital = data['items'][2]['title']
        hospital_address = data['items'][2]['address']['label']
        print("Hospital 3 Details -")
        print("")
        print("Name:", hospital)
        print("Address:", hospital_address)

    def get_hospital_four(self):
        data = self.retrieve_places()
        hospital = data['items'][3]['title']
        hospital_address = data['items'][3]['address']['label']
        hospital_num = data['items'][0]['contacts']['phone']['value']
        print("Hospital 4 Details -")
        print("")
        print("Name:", hospital)
        print("Address:", hospital_address)

    def get_hospital_five(self):
        data = self.retrieve_places()
        hospital = data['items'][4]['title']
        hospital_address = data['items'][4]['address']['label']
        print("Hospital 5 Details -")
        print("")
        print("Name:", hospital)
        print("Address:", hospital_address)


class Test(Widget):
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        wid = Button()
        wid.size = dp(200), dp(50)
        wid.text = "test"
        wid.font_size = sp(20)
        self.add_widget(wid)


class p(MDApp):

    def show_theme_picker(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()

    def build(self):
        self.theme_cls = ThemeManager()
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.accent_palette = 'DeepPurple'
        screen = Builder.load_string(screen_helper)
        return screen


p().run()
