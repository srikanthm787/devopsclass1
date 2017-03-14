# Defines our Vagrant environment
#
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  # create mgmt node
  config.vm.define :mgmt do |mgmt_config|
      mgmt_config.vm.box = "centos/6"
      mgmt_config.vm.hostname = "mgmt"
      mgmt_config.vm.network :private_network, ip: "10.0.16.10"
      mgmt_config.vm.network "public_network"
      mgmt_config.vm.provider "virtualbox" do |vb|
        vb.memory = "1024"
      end
  end

  # create load balancer
  config.vm.define :lb do |lb_config|
      lb_config.vm.box = "centos/6"
      lb_config.vm.hostname = "lb"
      lb_config.vm.network :private_network, ip: "10.0.16.11"
      lb_config.vm.network "public_network"
      lb_config.vm.provider "virtualbox" do |vb|
        vb.memory = "256"
      end
  end

  # create some web servers
  # https://docs.vagrantup.com/v2/vagrantfile/tips.html
  (1..2).each do |i|
    config.vm.define "web#{i}" do |node|
        node.vm.box = "ubuntu/trusty64"
        node.vm.hostname = "web#{i}"
        node.vm.network :private_network, ip: "10.0.16.2#{i}"
	node.vm.network "forwarded_port", guest: 80, host: 80
        node.vm.network "public_network"
	node.vm.provider "virtualbox" do |vb|
          vb.memory = "256"
        end
    end
  end
end
