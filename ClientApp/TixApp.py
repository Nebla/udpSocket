from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from functools import partial
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
import rsa
import requests
import subprocess
import webbrowser
import ConfigParser
import sys
import json
import keygeneration
import os, ctypes, platform
import subprocess
import shutil
import base64

sys.path.append('./InstallerFiles/')

Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '350')

# Tomo data del archivo de configuracion
config = ConfigParser.ConfigParser()
config.read('tixapp.cfg')
config.get("TiXClient", "tixBaseUrl")
config.get("TiXClient", "tixBaseUrl")
tixBaseUrl = config.get("TiXClient", "tixBaseUrl")
installDirUnix = config.get("TiXClient", "installDirUnix")


installationPath = os.getcwd()

globalUsername = ""
globalUserId = ""
globalUserPassword = ""
globalUserInstallations = []
globalPlatformName = platform.system()
globalIsAdmin = False

class LoginScreen(BoxLayout): #BoxLayout para poner arriba el form y abajo el boton de aceptar
  def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        self.analyze_is_admin()

        if platform.system() == "Darwin" and not os.getcwd().startswith("/Applications"):
          self.show_run_on_apps_popup()
        else:
          if os.path.exists(installDirUnix):
            self.show_already_installed_popup()
          else:
            self.show_install_form()

  def analyze_is_admin(self):
    try:
      is_admin = os.getuid() == 0
    except AttributeError:
      is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    global globalIsAdmin
    globalIsAdmin = is_admin

  def show_install_form(self):
    self.orientation = 'vertical'
    self.spacing='10sp'

    headerLayout = BoxLayout(orientation='horizontal')
    headerLabelsLayout = BoxLayout(orientation='vertical')

    headerLabelsLayout.add_widget(Label(text='Proyecto TiX', font_size=24))

    headerLabelsLayout.add_widget(Label(text='Iniciar sesion', font_size=18))

    headerLayout.add_widget(headerLabelsLayout)
    headerLayout.add_widget(Image(source='./images/LogoTiX.png'))
    self.add_widget(headerLayout)

    form = GridLayout(cols=2)
    form.add_widget(Label(text='Usuario'))
    self.username = TabTextInput(multiline=False)
    form.add_widget(self.username) #Username field
    form.add_widget(Label(text='Password'))
    self.password = TabTextInput(password=True, multiline=False) #Password field
    self.username.set_next(self.password)
    form.add_widget(self.password)
    self.add_widget(form)
    loginButton = Button(text="Conectar", size_hint_y=None, height='50sp',font_size=20)
    self.password.set_next(loginButton)
    self.add_widget(loginButton)
    loginButton.bind(on_press=partial(loginButtonOnClick,self.username,self.password)) #Accion que realizara el loginButton

  def show_run_on_apps_popup(self):
    btnclose = Button(text='Salir', size_hint_y=None, height='30sp')
    content = BoxLayout(orientation='vertical', spacing=10)
    content.add_widget(Label(text='Por favor, instale la aplicación en la carpeta de aplicaciones antes de correr este ejecutable'))
    content.add_widget(btnclose)
    popup = Popup(title='Error',content=content,size_hint=(None, None), size=(600, 200), auto_dismiss=False)
    btnclose.bind(on_release=partial(return_to_so,0))
    popup.open()

  def show_already_installed_popup(self):
    btnclose = Button(text='Salir', size_hint_y=None, height='30sp')
    content = BoxLayout(orientation='vertical', spacing=10)
    btncreateinstallation = Button(text='Desinstalar', size_hint_y=None,  size_hint_x=0.4, height='50sp', pos_hint={'center_x': 0.5})
    btncreateinstallation.bind(on_press=deleteExistingInstallation)
    content.add_widget(Label(text='Usted ya posee una instalacion de TiX en esta PC.'))
    content.add_widget(btncreateinstallation)
    content.add_widget(btnclose)
    popup = Popup(title='Error',content=content,size_hint=(None, None), size=(600, 200), auto_dismiss=False)
    btnclose.bind(on_release=partial(return_to_so,0))
    popup.open()

def loginButtonOnClick(username, password, instance):
        print 'Validando usuario ', username.text, '...'
        global globalUsername
        globalUsername = username.text
        global globalUserPassword
        globalUserPassword = password.text
                # tixBaseUrl = http://tix.innova-red.net:8080/tix/
                # tixBaseUrl = http://localhost:8080/tix/
        req = UrlRequest(tixBaseUrl + 'bin/api/authenticate?name='+ username.text+'&password='+password.text, on_success=create_new_installation, on_error=requestTimeOut)

def requestTimeOut(req, result):
                btnaccept = Button(text='Aceptar', size_hint_y=None, height='50sp')
                content = BoxLayout(orientation='vertical')
                content.add_widget(Label(text='Puede que el servidor de TiX no este funcionando correctamente.\nPor favor compruebe su conexion a internet y vuelva a intentarlo.'))
                content.add_widget(btnaccept)
                popup = Popup(title='Timeout Error',content=content,size_hint=(None, None), size=(600, 200), auto_dismiss=False)
                btnaccept.bind(on_press=popup.dismiss)
                popup.open()

def create_new_installation(req, result):
        try:
                jsonUserData = json.loads(result) # Parseo la respuesta JSON de la API de TiX
        except Exception, e:
                print "Malformed JSON server response. Exiting application..."
                exit(1)
        print jsonUserData
        if(result is not None and len(jsonUserData) > 0):
                global globalUserId
                globalUserId = jsonUserData['id']
                installationValues=[]
                userHasInstallations = False
                if(jsonUserData.get('installations') is not None and len(jsonUserData.get('installations')) > 0 ): #El usuario ya tiene instalaciones
                        userHasInstallations = True
                        for installation in jsonUserData.get('installations'):
                                installationValues.append(installation.replace('Installation: ', ''))

                        currentInstallationsString = ", ".join(installationValues)
                        global globalUserInstallations
                        globalUserInstallations = installationValues


                newInstallationInput = TabTextInput(halign='center',multiline=False,font_size=24)
                btnaccept = Button(text='Aceptar', size_hint_y=None, height='50sp')
                content = BoxLayout(orientation='vertical')
                content.add_widget(Label(text='Ingrese el nombre de la nueva instalacion:'))
                # spinner = Spinner(text=installationValues[0],values=installationValues,size_hint=(None, None),size=(100, 44),pos_hint={'center_x': .5, 'center_y': .5})
                # content.add_widget(spinner)
                content.add_widget(newInstallationInput) #Username field
                if(userHasInstallations):
                        content.add_widget(Label(halign='center',text='No repita el nombre de las instalaciones vigentes: \n' + currentInstallationsString))
                content.add_widget(btnaccept)
                popup = Popup(title='Instalador',content=content,size_hint=(None, None), size=(600, 300), auto_dismiss=False)
                btnaccept.bind(on_press=partial(select_installation,newInstallationInput, popup))
                popup.open()
        else:
                print 'Usuario invalido...'
                btnclose = Button(text='Cancelar', size_hint_y=None, height='30sp')
                content = BoxLayout(orientation='vertical', spacing=10)
                btncreateinstallation = Button(text='Crear nuevo usuario', size_hint_y=None,  size_hint_x=0.4, height='50sp', pos_hint={'center_x': 0.5})
                btncreateinstallation.bind(on_press=createNewInstallationWebsite)
                content.add_widget(Label(text='El usuario que ha ingresado es invalido o no existe.'))
                content.add_widget(btncreateinstallation)
                content.add_widget(btnclose)
                popup = Popup(title='Error',content=content,size_hint=(None, None), size=(600, 200), auto_dismiss=False)
                btnclose.bind(on_release=popup.dismiss)
                popup.open()

def select_installation(self, old_popup,instance):
        print 'Instalacion elegida: ', self.text
        print 'Validando nombre de instalacion... ', self.text, '...'
        if(self.text in globalUserInstallations):
                print 'ERROR: Instalacion repetida...'
                create_information_popup('Error','El nombre de la instalacion ya ha sido elegido previamente.', 'dismiss').open()
        else:
                old_popup.dismiss()

                if execute_installation() == 1:
                        installation_result_popup('No se ha podido completar la instalacion',1)

                publicKeyFile = open(installDirUnix + 'tix_key.pub','r')
                publicKey = rsa.PublicKey.load_pkcs1(publicKeyFile.read())

                # publicEncryptionKey = keygeneration.generateKeyPair(installDirUnix+'tix_key.priv',installDirUnix+'tix_key.pub')
                payload = {'user_id': str(globalUserId), 'password': globalUserPassword, 'installation_name': self.text, 'encryption_key': base64.b64encode(publicKey.save_pkcs1(format='PEM'))}
                headers = {'content-type': 'application/json'}

                r = requests.post(tixBaseUrl + 'bin/api/newInstallationPost', data=json.dumps(payload), headers=headers)
                try:
                        jsonUserData = json.loads(r.text) # Parseo la respuesta JSON de la API de TiX
                except Exception, e:
                        print "Malformed JSON server response. Exiting application..."
                        exit(1)

                if(r is not None and len(jsonUserData) > 0):
                        installation_result_popup('Instalacion Exitosa',0)
                else:
                        installation_result_popup('No se ha podido completar la instalacion',1)
                # print 'bin/api/newInstallation?user_id='+str(globalUserId)+'&password='+globalUserPassword+'&installation_name='+self.text+'&encryption_key='+publicEncryptionKey
                # req = UrlRequest(tixBaseUrl + 'bin/api/newInstallation?user_id='+str(globalUserId)+'&password='+globalUserPassword+'&installation_name='+self.text+'&encryption_key='+publicEncryptionKey, on_success=finish_installation, on_error=requestTimeOut)

def execute_installation():
        global globalPlatformName
        if globalPlatformName == "Linux":
                try:
                        subprocess.call(["gksudo", "echo 'Gaining root privileges..."]) #Test if ejecutable exists
                except OSError as e:
                        popup = create_information_popup('Error','Debe ejecutar este programa con permisos de adminsitrador', partial(return_to_so,1)).open()

                sys_return = subprocess.call(['gksudo','./installStartupUDPClient'])
                second_return = subprocess.Popen(['gksudo','/bin/bash', '/etc/init.d/startupAppCaller.sh'])
                print("about to ask for updater caller");
                sys_return = subprocess.call(['gksudo','./InstallerFiles/tix_updater_caller.sh'])
        if globalPlatformName == "Darwin":
                sys_return = os.system("""osascript -e 'do shell script "./installStartupUDPClient" with administrator privileges'""")
                # sys_return = os.system("sudo %s/installStartupUDPClient" % installationPath)
        return sys_return

def installation_result_popup(installation_return,sys_return):
        popup = create_information_popup('Proceso de instalacion',installation_return, partial(return_to_so,sys_return))
        # btnaccept.bind(on_press=partial(return_to_so,sys_return))
        # content.add_widget(btnaccept)
        popup.open()
        # sys.exit(sys_return)

def return_to_so(sys_return, instance):
        sys.exit(sys_return)

def create_information_popup(title, information, button_action):
        btnaccept = Button(text='Aceptar', size_hint_y=None, height='50sp')
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=information))
        content.add_widget(btnaccept)
        popup = Popup(title=title,content=content,size_hint=(None, None), size=(600, 200), auto_dismiss=False)
        if(button_action == 'dismiss'):
                btnaccept.bind(on_press=popup.dismiss)
        else:
                btnaccept.bind(on_press=button_action)
        return popup

def deleteExistingInstallation(self):
        global globalPlatformName
        if globalPlatformName == "Linux":
                try:
                        subprocess.call(["gksudo", "echo 'Gaining root privileges..."]) #Test if ejecutable exists
                except OSError as e:
                        popup = create_information_popup('Error','Debe ejecutar este programa con permisos de adminsitrador', partial(return_to_so,1)).open()

                sys_return = subprocess.call(['gksudo','python ./InstallerFiles/uninstallStartupUDPClient.py'])

        if globalPlatformName == "Darwin":
                # sys_return = os.system("launchctl remove com.user.loginscript")
                # if os.path.isfile("~/Library/LaunchAgents/com.user.loginscript.plist"):
                #         os.remove("~/Library/LaunchAgents/com.user.loginscript.plist")
                # if os.path.exists("/etc/TIX/"):
                #         shutil.rmtree("/etc/TIX/")

                sys_return = os.system("""osascript -e 'do shell script "./uninstallStartupUDPClient" with administrator privileges'""")

        if(sys_return == 0): # Call to installation procedure
                installation_return = 'Se ha borrado con exito la desinstalacion de TiX. Retornando al SO...'
                sys_return = 0
        else:
                installation_return = 'Ha ocurrido un error en el proceso de desinstalacion y el programa se cerrara.'
                sys_return = 1

        popup = create_information_popup('Proceso de instalacion',installation_return, partial(return_to_so,sys_return)).open()

def createNewInstallationWebsite(self):
        webbrowser.open(tixBaseUrl)

class TabTextInput(TextInput):
        def __init__(self, *args, **kwargs):
                self.next = kwargs.pop('next', None)
                super(TabTextInput, self).__init__(*args, **kwargs)

        def set_next(self, next):
                self.next = next

        def _keyboard_on_key_down(self, window, keycode, text, modifiers):
                key, key_str = keycode
                if key in (9, 13) and self.next is not None:
                        self.next.focus = True
                        if(isinstance(self.next, TabTextInput)):
                                self.next.select_all()
                else:
                        super(TabTextInput, self)._keyboard_on_key_down(window, keycode, text, modifiers)

class TiXApp(App):
   def build(self):
     return LoginScreen()

if __name__ == '__main__':
  TiXApp().run()
