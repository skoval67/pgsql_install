#!/home/sergey/repo/pgsql_install/venv/bin/python3

import sys
from fabric import Connection

HOST_USER = "admin"
POSTGRES_VERSON = 16

commands = {
  "debian": [
    "sudo apt update && sudo apt install -y postgresql-{POSTGRES_VERSON}",
    f"sudo sed -i \"/listen_address/c\listen_addresses = '0.0.0.0'\" /etc/postgresql/{POSTGRES_VERSON}/main/postgresql.conf",
    "sudo systemctl restart postgresql",
    "cd ~postgres && sudo -u postgres psql -c 'SELECT 1'"
  ],
  "rhel fedora": [
    "sudo yum update -y && sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-`rpm -E %{rhel}`-x86_64/pgdg-redhat-repo-latest.noarch.rpm",
    "sudo dnf module disable -y postgresql && sudo dnf clean all",
    f"sudo yum makecache -y && sudo yum install -y postgresql{POSTGRES_VERSON}-server postgresql{POSTGRES_VERSON}-contrib && sudo /usr/pgsql-{POSTGRES_VERSON}/bin/postgresql-{POSTGRES_VERSON}-setup initdb",
    f"sudo systemctl enable postgresql-{POSTGRES_VERSON} && sudo systemctl start postgresql-{POSTGRES_VERSON}",
    "sudo cd ~postgres && sudo -u postgres psql -c 'SELECT 1'"
  ]
}

def Usage():
  print("Usage: pginst Ip or Fqdn")

def install_pgsql(target):
  conn = Connection(host=target, user=HOST_USER)

  try:
    os_release_id = conn.run(". /etc/os-release && echo \"$ID_LIKE\"", hide=True).stdout.strip()
    if os_release_id == '':
      os_release_id = conn.run(". /etc/os-release && echo \"$ID\"", hide=True).stdout.strip()

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