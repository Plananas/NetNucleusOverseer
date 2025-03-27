import json
import threading
import secrets

from flask import jsonify, request, redirect, url_for, g
from flask import Blueprint, render_template

from App.Backend.Repositories.ClientRepository import ClientRepository
from App.Backend.Repositories.ProgramRepository import ProgramRepository
from App.Backend.Repositories.SiteRepository import SiteRepository

class ClientController:

    main = Blueprint(
        "main",
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    def __init__(self):
        self.main.add_url_rule(
            '/do_login',
            'do_login',
            self.do_login,
            methods=['POST'])

        self.lock = threading.Lock()
        #self.server = server
        #print(self.server.id)
        self.session_store = {}

        # @self.main.before_request
        # def check_login():
        #     print("check_login")
        #     if request.endpoint not in ['main.login', 'main.do_login', 'static']:
        #         login_token = request.cookies.get('login')
        #         if not login_token or login_token not in self.session_store:
        #             return redirect(url_for('main.login'))
        #         g.user = self.session_store[login_token]


    def getBlueprint(self):
        return self.main


    @staticmethod
    @main.route('/login')
    def login():
        login_failed = request.args.get('login_failed', 'false') == 'true'
        return render_template('login.html', login_failed=login_failed)


    def do_login(self):
        #FIXME change login logic to work with the saas
        username = request.form.get('username')
        password = request.form.get('password')

        #if self.server.confirm_user(self.server, username, password):  # Replace with real logic
        unique_token = secrets.token_hex(16)  # Generate a secure random token
        self.session_store[unique_token] = username  # Save the token associated with the user

        response = redirect(url_for('main.home'))
        response.set_cookie('login', unique_token, max_age=3600, httponly=True, secure=True)  # Secure cookie settings
        return response
        # else:
        #     return redirect(url_for('main.login', login_failed='true'))


    @staticmethod
    @main.route('/dashboard')
    def home():
        """Render the home page with sites data."""
        site_repository = SiteRepository()  # Use the repository for sites instead of clients
        sites = site_repository.get_all_sites()  # Retrieve all site objects
        sites_as_dict = [site.to_dict() for site in sites]

        # Calculate the number of sites that are online
        online_site_count = sum(1 for site in sites if site.online)

        return render_template('home.html', sites=sites_as_dict, online_site_count=online_site_count)


    @staticmethod
    @main.route('/api/clients', methods=['GET'])
    def get_clients():
        """Endpoint to return the list of clients."""
        client_repository = ClientRepository()

        # Convert list of ClientModel instances to list of dictionaries
        clients = [client.to_dict() for client in client_repository.get_all_clients()]

        return jsonify(clients), 200

    @staticmethod
    @main.route('/api/sites', methods=['POST'])
    def update_sites():
        """Endpoint to update or create sites."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No input data provided"}), 400

            # Determine if we received a list of sites or a single site
            if isinstance(data, list):
                saved_sites = []
                for site_data in data:
                    # Create a SiteModel instance from the provided JSON data.
                    site = SiteModel(**site_data)
                    site.save()
                    saved_sites.append(site.to_dict())
                return jsonify({"status": "success", "sites": saved_sites}), 200
            elif isinstance(data, dict):
                site = SiteModel(**data)
                site.save()
                return jsonify({"status": "success", "site": site.to_dict()}), 200
            else:
                return jsonify({"error": "Invalid data format; expected a JSON object or list"}), 400

        except Exception as e:
            logging.exception("Error updating sites")
            return jsonify({"error": str(e)}), 500


    @staticmethod
    @main.route('/clients', methods=['GET'])
    def get_clients_page():
        """Endpoint to return the list of clients."""
        client_repository = ClientRepository()

        # Convert list of ClientModel instances to list of dictionaries
        clients = [client.to_dict() for client in client_repository.get_all_clients()]

        return render_template('clients.html', clients=clients)


    @staticmethod
    @main.route('/settings', methods=['GET'])
    def get_settings_page():
        return render_template('settings.html')


    @staticmethod
    @main.route('/rules', methods=['GET'])
    def get_rules_page():
        return render_template('rules.html')


    @staticmethod
    @main.route('/default-apps', methods=['GET'])
    def get_default_apps_page():
        return render_template('default-apps.html')


    @staticmethod
    @main.route('/clients/<string:mac_address>', methods=['GET'])
    def get_client_by_mac_page(mac_address):
        """Endpoint to return a single client by name."""
        client_repository = ClientRepository()
        program_repository = ProgramRepository()

        # Attempt to retrieve the client by nickname
        client = client_repository.get_client_by_mac_address(mac_address)[0]

        programs = [program.to_dict() for program in client.get_installed_programs()]
        try:
            client.firewall_status = json.loads(client.firewall_status)
        except Exception:
            client.firewall_status = {}
        try:
            client.bitlocker_status = json.loads(client.bitlocker_status)
        except Exception:
            client.bitlocker_status = {}

        if client is None:
            return jsonify({"error": f"No client found with nickname '{mac_address}'"}), 404

        # Convert the client to a dictionary
        return render_template('client.html', client=client, programs=programs)


    @main.route('/site/<string:uuid>', methods=['GET'])
    def get_site_page(uuid):
        """Endpoint to return a single site and its associated clients with installed programs."""
        site_repository = SiteRepository()
        client_repository = ClientRepository()
        program_repository = ProgramRepository()

        # Retrieve the site by UUID (assuming get_site_by_uuid returns a list)
        sites = site_repository.get_site_by_uuid(uuid)
        if not sites:
            return jsonify({"error": f"No site found with uuid '{uuid}'"}), 404
        site = sites[0]

        # Retrieve clients for the site using a repository method (you may need to implement this)
        clients = client_repository.get_clients_by_site_id(site.id)

        # For each client, decode status fields and fetch installed programs
        for client in clients:
            try:
                client.firewall_status = json.loads(client.firewall_status)
            except Exception:
                client.firewall_status = {}
            try:
                client.bitlocker_status = json.loads(client.bitlocker_status)
            except Exception:
                client.bitlocker_status = {}

            programs = program_repository.get_programs_by_client_uuid(client.uuid)
            client.programs = [program.to_dict() for program in programs]

        return render_template('site.html', site=site, clients=clients)


    @staticmethod
    @main.route('/api/clients/name/<string:client_name>', methods=['GET'])
    def get_client_by_name(client_name):
        """Endpoint to return a single client by name."""
        client_repository = ClientRepository()

        # Attempt to retrieve the client by nickname
        client = client_repository.get_client_by_nickname(client_name)

        if client is None:
            return jsonify({"error": f"No client found with nickname '{client_name}'"}), 404

        # Convert the client to a dictionary
        return jsonify(client.to_dict()), 200

    @staticmethod
    @main.route('/api/site', methods=['PUT'])
    def create_site():
        """Endpoint to return a single client by name."""
        #TODO take a json and use some kind of service or model to create it

        # Attempt to retrieve the client by nickname
        client = client_repository.get_client_by_nickname(client_name)

        if client is None:
            return jsonify({"error": f"No client found with nickname '{client_name}'"}), 404

        # Convert the client to a dictionary
        return jsonify(client.to_dict()), 200


    def shutdown_client(self):
        # data = request.get_json()
        # command = 'shutdown'
        #
        # if data.get('mac'):
        #     command += " " + str(data.get('mac'))
        #
        # response = self.server.enter_command('shutdown')

        #TODO implement feature
        return jsonify({"message": 'implement feature'}), 200


    def scan_for_upgrades(self):
        #response = self.server.enter_command('upgrades')
        #TODO contact site

        return jsonify({"message": "implement feature"}), 200


    def get_upgrades(self):
        #response = self.server.enter_command('upgrade all')
        #TODO contact site

        return jsonify({"message": "implement feature"}), 200


    def install_software(self):
        # data = request.get_json()
        # command = "install " + str(data.get('software'))
        #
        # if data.get('mac'):
        #     command += " " + str(data.get('mac'))
        #response = self.server.enter_command(command)
        #TODO contact site


        return jsonify({"message": "implement feature"}), 200