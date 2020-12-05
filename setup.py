# only for windows
import getpass
USER_NAME = getpass.getuser()

def add_to_startup(file_path=""):
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
        print(file_path)
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME 
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(r'call C:\Users\basti\Anaconda3\condabin\conda.bat activate base;cd C:\Users\basti\git\HandTracking4Sohan;start cmd/k python "" %s' % file_path)
        print('bat file written')

if __name__ == "__main__":
    file_path = r'C:\Users\basti\git\HandTracking4Sohan\CameraInterface.py'
    add_to_startup(file_path)