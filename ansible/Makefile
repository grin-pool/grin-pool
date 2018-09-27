
default: build

PUB_IP := "18.206.45.124"
INT_IP := "172.31.70.105"
USER := "ubuntu"

clean:
	rm -rf prereqs
	rm -rf kubespray
	rm -f access
	rm -f pool
	rm -f grin

access:
	ansible-playbook -i inventory --tags "access" --ask-pass --ask-sudo-pass site.yaml 
	touch access

prereqs: access
	ansible-playbook -i inventory --tags "prereqs" site.yaml
	touch prereqs

kubespray: access prereqs
	git clone https://github.com/kubernetes-incubator/kubespray.git
	cd kubespray && virtualenv venv
	cd kubespray && . venv/bin/activate && pip install -r requirements.txt
	cd kubespray && mkdir -p inventory/mycluster
	cd kubespray && cp -rfp inventory/sample/* inventory/mycluster
	cd kubespray && CONFIG_FILE=inventory/mycluster/hosts.ini python3 contrib/inventory_builder/inventory.py ${IPS}
	cd kubespray && . venv/bin/activate && ansible-playbook -u ${USER} --become -i inventory/mycluster/hosts.ini  cluster.yml

grin: kubespray
	ansible-playbook -i inventory --tags "grin" site.yaml
	touch grin

pool: grin
	ansible-playbook -i inventory --tags "pool" site.yaml
	touch pool

build: access kubespray grin
	make prereqs
	make access
	make kubespray
	make grin
	make pool
