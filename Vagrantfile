# -*- mode: ruby -*-
# vi: set ft=ruby :


VAGRANTFILE_API_VERSION = "2"

CLOUD_CONFIG_USERNAME = "ansible"
CLOUD_CONFIG_URL = "10.0.0.10:5000"
CLOUD_CONFIG_KEY = "~/.ssh/id_rsa.pub"
CLOUD_CONFIG_TOKEN = "26758c32-3421-4f3d-9603-e4b5337e7ecc"
CLOUD_CONFIG_GEN = File.dirname(__FILE__) + "/cephlcmlib/cephlcmlib/cli/cloud_config.py"
CLOUD_CONFIG_FILE = `./devenv/vagrant-cloud-config.py #{CLOUD_CONFIG_USERNAME} #{CLOUD_CONFIG_URL} #{CLOUD_CONFIG_KEY} #{CLOUD_CONFIG_TOKEN}`

at_exit do
  File.delete CLOUD_CONFIG_FILE
end


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box_check_update = false
  config.ssh.forward_agent   = true

  config.vm.define "default", primary: true do |devbox|
    devbox.vm.box = "ubuntu/xenial64"
    devbox.vm.hostname = "cephlcm"
    devbox.vm.network "private_network", ip: "10.0.0.10"
    devbox.vm.synced_folder ".", "/vagrant", type: "nfs"

    devbox.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 3092
      vb.cpus = 2
    end

    if Vagrant.has_plugin?("vagrant-cachier")
      devbox.cache.scope = :box
      devbox.cache.enable :apt
      devbox.cache.enable :apt_lists
      devbox.cache.enable :bower
      devbox.cache.enable :npm
      devbox.cache.enable :generic, {
        "pip" => { :cache_dir => ".cache/pip" },
        "ccache" => { :cache_dir => ".ccache"  }
      }
      devbox.cache.synced_folder_opts = {
        type: :nfs, mount_options: ['rw', 'vers=3', 'tcp', 'nolock']
      }
    else
      print "vagrant-cachier plugin has not been found."
      print "You can install it by `vagrant plugin install vagrant-cachier`"
    end

    if Vagrant.has_plugin?("vagrant-host-shell")
      devbox.vm.provision :host_shell do |host_shell|
        host_shell.inline = "ansible-galaxy install -r devenv/requirements.yaml -p devenv/galaxy"
      end
    else
      abort "You have to install vagrant-host-shell plugin to continue"
    end

    devbox.vm.provision "ansible" do |ansible|
      ansible.playbook = "devenv/devbox.yaml"
    end
  end

  config.vm.define "devbox", primary: false, autostart: false do |libvirt_devbox|
    libvirt_devbox.vm.box = "yk0/ubuntu-xenial"
    libvirt_devbox.vm.hostname = "cephlcm"
    libvirt_devbox.vm.network "private_network", ip: "10.20.0.10"
    libvirt_devbox.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["rw", "vers=3", "noatime", "async"]

    libvirt_devbox.vm.provider :libvirt do |lv|
      lv.memory = 3092
      lv.cpus = 2
      lv.nested = true
      lv.cpu_mode = "host-passthrough"
      lv.machine_virtual_size = 60
    end

    if Vagrant.has_plugin?("vagrant-cachier")
      libvirt_devbox.cache.scope = :box
      libvirt_devbox.cache.enable :apt
      libvirt_devbox.cache.enable :apt_lists
      libvirt_devbox.cache.enable :bower
      libvirt_devbox.cache.enable :npm
      libvirt_devbox.cache.enable :generic, {
        "pip" => { :cache_dir => ".cache/pip" },
        "ccache" => { :cache_dir => ".ccache"  }
      }
      libvirt_devbox.cache.synced_folder_opts = {
        type: :nfs, mount_options: ['rw', 'vers=3', 'noatime', 'async']
      }
    else
      print "vagrant-cachier plugin has not been found."
      print "You can install it by `vagrant plugin install vagrant-cachier`"
    end

    if Vagrant.has_plugin?("vagrant-host-shell")
      libvirt_devbox.vm.provision :host_shell do |host_shell|
        host_shell.inline = "ansible-galaxy install -r devenv/requirements.yaml -p devenv/galaxy"
      end
    else
      abort "You have to install vagrant-host-shell plugin to continue"
    end

    libvirt_devbox.vm.provision "ansible" do |ansible|
      ansible.playbook = "devenv/devbox.yaml"
    end
  end

  ["mon", "osd0", "osd1", "osd2"].each_with_index do |host, idx|
    config.vm.define "#{host}", autostart: false do |client|
      client.vm.box = "ubuntu/trusty64"
      client.vm.hostname = "ceph-#{host}"
      client.vm.network "private_network", ip: "10.0.0.2#{idx}"

      # http://foo-o-rama.com/vagrant--stdin-is-not-a-tty--fix.html
      client.vm.provision "fix-no-tty", type: "shell" do |s|
        s.privileged = false
        s.inline = "sudo sed -i '/tty/!s/mesg n/tty -s \\&\\& mesg n/' /root/.profile"
      end

      client.vm.provision "copy-cloud-config",
        type: "file",
        source: CLOUD_CONFIG_FILE,
        destination: "/tmp/user-data"
      client.vm.provision "cloud-init", type: "shell" do |s|
        s.privileged = true
        s.inline = "mv /tmp/user-data /var/lib/cloud/seed/nocloud-net/user-data && rm -r /var/lib/cloud/instances/* && cloud-init init --local && cloud-init init && cloud-init modules"
      end

      client.vm.provider "virtualbox" do |vb|
        vb.gui = false
        vb.memory = 512
        vb.cpus = 2

        (0..1).each do |d|
            disk_name = "#{host}-#{idx}-#{d}"
            vb.customize ["createhd",
                          "--filename", disk_name,
                          "--size", "11000"] unless File.exist?("#{disk_name}.vdi")
            vb.customize ["storageattach", :id,
                          '--storagectl', "SATAController",
                          "--port", 3 + d,
                          "--device", 0,
                          "--type", "hdd",
                          "--medium", "#{disk_name}.vdi"]
        end

      end
    end
  end
end
