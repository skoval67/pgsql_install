terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  folder_id = var.folder_id
  zone      = "ru-central1-a"
}

variable "folder_id" {
  type = string
}

variable "image-id" {
  type = string
}

variable "site_name" {
  type        = string
  description = "DNS-имя сайта"
}

resource "yandex_vpc_network" "network1" {}

resource "yandex_vpc_subnet" "subnet" {
  network_id     = yandex_vpc_network.network1.id
  name           = "subnet"
  v4_cidr_blocks = ["192.168.0.0/24"]
}

resource "yandex_compute_instance" "vm-1" {
  name        = "vm1"
  platform_id = "standard-v1"
  zone        = "ru-central1-a"

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 5
  }

  scheduling_policy {
    preemptible = true
  }

  boot_disk {
    initialize_params {
      image_id = var.image-id
      size     = 10
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
    nat       = true
  }

  metadata = {
    user-data = "${file("users.yml")}"
  }
}

resource "yandex_dns_zone" "external_zone" {
  name        = "externalzone"
  description = "externalzone"
  zone        = "${var.site_name}."
  public      = true
}

resource "yandex_dns_recordset" "rs1" {
  zone_id = yandex_dns_zone.external_zone.id
  name    = "pg.${var.site_name}."
  type    = "A"
  ttl     = 200
  data    = [yandex_compute_instance.vm-1.network_interface.0.nat_ip_address]
}

output "ip" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}