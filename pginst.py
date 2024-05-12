#!/home/sergey/repo/pgsql_install/venv/bin/python3

import os, sys
from fabric import Connection

HOST_USER = "admin"
POSTGRES_VERSION = 10.5
POSTGRES_PASS = os.popen("openssl rand -base64 16").read().strip()
MYIP = os.popen("curl https://ident.me").read().strip()

Requirements = {
  "debian": [
    "sudo apt update && sudo apt install -y gcc build-essential zlib1g-dev libreadline6-dev libicu-dev pkg-config"
  ],
  "redhat": [
    "sudo yum update -y && sudo yum install -y make gcc zlib-devel readline-devel libicu-devel"
  ]
}

Installations = [
  f"curl https://ftp.postgresql.org/pub/source/v{POSTGRES_VERSION}/postgresql-{POSTGRES_VERSION}.tar.gz -O",
  f"tar xzf postgresql-{POSTGRES_VERSION}.tar.gz",
  f"cd postgresql-{POSTGRES_VERSION} && ./configure && make && sudo make install",
  f"sudo useradd -p $(openssl passwd -1 {POSTGRES_PASS}) postgres && echo Postgres user password: {POSTGRES_PASS}",
  "sudo mkdir -p /usr/local/pgsql/data",
  "sudo chown postgres /usr/local/pgsql/data",
  "sudo -u postgres /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data",
  "sudo sed -i \"/listen_address/c\listen_addresses = '0.0.0.0'\" /usr/local/pgsql/data/postgresql.conf",
  f"sudo sed -i '/# IPv6 local connections:/i host    all             all             {MYIP}/32         trust' /usr/local/pgsql/data/pg_hba.conf",
  f"sudo mv /home/{HOST_USER}/postgresql.service /usr/lib/systemd/system/",
  "sudo systemctl daemon-reload && sudo systemctl enable postgresql && sudo systemctl start postgresql",
  "sudo -u postgres /usr/local/pgsql/bin/psql -c 'select version();'"
]

def Usage():
  print("Usage: pginst.py 'Ip or Fqdn'")

def install_pgsql(target):
  conn = Connection(host=target, user=HOST_USER)

  try:
    os_release_id = conn.run(". /etc/os-release && echo \"$ID_LIKE\"", hide=True).stdout.strip()
    if os_release_id == '':
      os_release_id = conn.run(". /etc/os-release && echo \"$ID\"", hide=True).stdout.strip()
    if 'fedora' in os_release_id:
      os_release_id = "redhat"

    if os_release_id == "redhat":
      Installations.insert(10, "sudo chcon -t systemd_unit_file_t /usr/lib/systemd/system/postgresql.service && sudo restorecon -vF /usr/lib/systemd/system/postgresql.service")

    for cmd in Requirements[os_release_id]:
      conn.run(cmd)

    conn.put('postgresql.service')

    for cmd in Installations:
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
