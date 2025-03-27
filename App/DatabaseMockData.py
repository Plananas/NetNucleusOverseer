import sqlite3
import uuid
import json
import random

# Utility functions
def random_mac_address():
    """Generate a random MAC address."""
    return ":".join("{:02X}".format(random.randint(0, 255)) for _ in range(6))

def random_ip_address():
    """Generate a random local IP address in the range 192.168.1.x."""
    return f"192.168.1.{random.randint(2, 254)}"

def random_storage():
    """Return a random storage usage string like '30/128'."""
    used = random.randint(10, 100)
    total = random.choice([128, 256, 512])
    return f"{used}/{total}"

def sample_firewall_status():
    """Return a sample firewall status as a JSON string."""
    status = {
        "Domain": random.choice([True, False]),
        "Private": random.choice([True, False]),
        "Public": random.choice([True, False])
    }
    return json.dumps(status)

def sample_bitlocker_status():
    """Return a sample bitlocker status as a JSON string."""
    statuses = [
        {
            "DeviceID": "C:",
            "ProtectionStatus": random.choice(["On (Protected)", "Off (Not Protected)"]),
            "EncryptionMethod": random.choice(["XTS-AES 256-bit", "AES 128-bit"])
        },
        {
            "DeviceID": "D:",
            "ProtectionStatus": random.choice(["On (Protected)", "Off (Not Protected)"]),
            "EncryptionMethod": random.choice(["XTS-AES 256-bit", "AES 128-bit"])
        }
    ]
    return json.dumps(statuses)

def sample_windows_version():
    """Return a sample Windows version and version number."""
    version = random.choice(["10", "11"])
    version_number = random.choice(["10.0.19042", "10.0.22000", "10.0.18363"])
    return version, version_number

def sample_installed_programs():
    """Return a list of sample installed programs for a client."""
    software_options = [
        ("Chrome", "95.0", "96.0"),
        ("Firefox", "89.0", "90.0"),
        ("Office", "2019", "2021"),
        ("Slack", "4.20", "4.25"),
        ("Zoom", "5.6", "5.7")
    ]
    # Choose 2 random programs
    return random.sample(software_options, 2)

def add_mock_data():
    """Insert mock data into the database."""
    # Connect to the database (adjust path if needed)
    conn = sqlite3.connect('overseer.db')
    cursor = conn.cursor()

    # Insert 5 sites
    site_ids = []
    for i in range(1, 6):
        site_uuid = str(uuid.uuid4())
        site_nickname = f"Site {i}"
        site_online = random.choice([0, 1])
        site_mac = random_mac_address()
        site_ip = random_ip_address()

        cursor.execute('''
            INSERT INTO sites (uuid, nickname, online, mac_address, ip_address)
            VALUES (?, ?, ?, ?, ?)
        ''', (site_uuid, site_nickname, site_online, site_mac, site_ip))
        site_id = cursor.lastrowid
        site_ids.append(site_id)
        print(f"Inserted {site_nickname} with id {site_id}")

        # For each site, insert a few clients (2 to 3 clients per site)
        num_clients = random.randint(2, 3)
        for j in range(1, num_clients + 1):
            client_uuid = str(uuid.uuid4())
            client_mac = random_mac_address()
            client_nickname = f"Client {i}-{j}"
            shutdown = random.choice([0, 1])
            storage = random_storage()
            firewall_status = sample_firewall_status()
            windows_version, windows_version_number = sample_windows_version()
            bitlocker_status = sample_bitlocker_status()
            current_user = f"User_{i}_{j}"

            cursor.execute('''
                INSERT INTO clients (uuid, mac_address, nickname, shutdown, storage, firewall_status,
                                     windows_version, windows_version_number, bitlocker_status, current_user, site_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_uuid, client_mac, client_nickname, shutdown, storage, firewall_status,
                windows_version, windows_version_number, bitlocker_status, current_user, site_id
            ))
            print(f"  Inserted {client_nickname} under {site_nickname}")

            # Insert a few installed programs for this client (2 programs per client)
            programs = sample_installed_programs()
            for program in programs:
                name, current_version, available_version = program
                cursor.execute('''
                    INSERT INTO installed_programs (client_uuid, name, current_version, available_version)
                    VALUES (?, ?, ?, ?)
                ''', (client_uuid, name, current_version, available_version))
                print(f"    Inserted program {name} for {client_nickname}")

    conn.commit()
    conn.close()
    print("Test data insertion complete.")

if __name__ == "__main__":
    addmockData()
