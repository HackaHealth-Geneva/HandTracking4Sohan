import serial
import serial.tools.list_ports

def connect_to_arduino_if_exist():
    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'Arduino' in p.description  # may need tweaking to match new arduinos
    ]
    try:
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            warnings.warn('Multiple Arduinos found - using the first')
        ser = serial.Serial(port =arduino_ports[0], baudrate ="9600");
    except:
        print("Arduino is not connected")
        ser = []
    return ser


ser = connect_to_arduino_if_exist()

# ser = serial.Serial('COM3', 9600)
data = 0



while True:
    if ser:
        data = ser.readline()
        print('data ' + str(data[0]))
    
