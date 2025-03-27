import threading

from flask import Flask

from App.MainController import ClientController
import App.SetupDB as SetupDB

#global server

if __name__ == '__main__':
    #server = ServerProcess()
    #print(server.id)
    SetupDB.setup_database()

    client_controller = ClientController()

    print("run thread")
    #threading.Thread(target=client_controller.server.run, daemon=True).start()

    app = Flask(__name__, static_folder='static', template_folder='templates')
    LOGIN_COOKIE_KEY = 'login'
    blueprint = client_controller.getBlueprint()
    app.register_blueprint(blueprint)
    #Debug mode won't let you use the application
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)



