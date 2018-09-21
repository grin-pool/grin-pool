#!/bin/bash
ansible-playbook -i inventory --ask-pass --ask-sudo-pass site.yaml
