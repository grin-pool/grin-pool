
default: build

EXT_IP := "13.52.54.132 13.57.107.221 13.57.87.74"
INT_IP := 10.1.1.177
USER := "ubuntu"

clean:
	rm -rf prereqs
	rm -rf kubespray
	rm -f access
	rm -f pool
	rm -f grin
	rm -f site.retry

python:
	ssh ${USER}@${EXT_IP} sudo apt-get -y install python python-apt

access:
	ansible-playbook -i inventory --tags "access" -u ${USER} --ask-pass --ask-sudo-pass site.yaml 
	touch access

prereqs: access python
	ansible-playbook -i inventory -u ${USER} --tags "prereqs" site.yaml
	touch prereqs

kubespray: access prereqs
	git clone https://github.com/kubernetes-incubator/kubespray.git
	cd kubespray && virtualenv venv
	cd kubespray && . venv/bin/activate && pip install -r requirements.txt
	cd kubespray && mkdir -p inventory/mycluster
	cd kubespray && cp -rfp inventory/sample/* inventory/mycluster
	cd kubespray && CONFIG_FILE=inventory/mycluster/hosts.ini python3 contrib/inventory_builder/inventory.py ${EXT_IP}
	sed -i 's/ip=${EXT_IP}/ip=${INT_IP}/' kubespray/inventory/mycluster/hosts.ini
	cd kubespray && . venv/bin/activate && ansible-playbook -u ${USER} --become -i inventory/mycluster/hosts.ini  cluster.yml

grin: kubespray
	ansible-playbook -i inventory -u ${USER} --tags "grin" site.yaml
	touch grin

pool: grin
	ansible-playbook -i inventory -u ${USER} --tags "pool" site.yaml
	touch pool

build: access kubespray grin
	make prereqs
	make access
	make kubespray
	make grin
	make pool
