# #!/usr/bin/python

import sys
from fabric import Connection

HOST_USER = "admin"
POSTGRES_VERSON = 15

commands = {
  "debian": [
    "sudo apt update",
    f"sudo apt install -y postgresql-{POSTGRES_VERSON}",
    f"sudo sed -i \"/listen_address/c\listen_addresses = '0.0.0.0'\" /etc/postgresql/{POSTGRES_VERSON}/main/postgresql.conf",
    "sudo systemctl restart postgresql",
    "cd ~postgres && sudo -u postgres psql -c 'SELECT 1'"
  ],
  "centos": []
}

def Usage():
  print("Usage: pginst Ip or Fqdn")

def install_pgsql(target):
  conn = Connection(host=target, user=HOST_USER)
  try:
    os_release_id = "debian"
    for cmd in commands[os_release_id]:
      conn.run(cmd)
  except Exception as err:
    print(f"{err}, {type(err)}")

def main(args=[]):
  if not args :
    Usage()
  else:
    install_pgsql(args[0])

if __name__ == "__main__":
  main(sys.argv[1:])