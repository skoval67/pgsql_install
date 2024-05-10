terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  folder_id = "b1g9cj9hkc9nb77qmv8f"
  zone      = "ru-central1-a"
}

variable "image-id" {
  type = string
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

output "ip" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}