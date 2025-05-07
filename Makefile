-include .env
export

PACKAGE=purem_sandbox
BENCHMARKS_PLATFORM=Darwin-CPython-3.11-64bit
EC2_SSH_KEY_NAME=purem_benchmarks_ssh_key
TEST=00
LAST_TEST_ID=00

all:
	@echo "Nothing to do by default. Use 'make test' or 'make plot'."
.PHONY: all

benchmarks_arm:
	@timestamp=$$(date +%Y%m%d_%H%M%S) && \
    	for size in 20000 30000 50000 100000 150000 200000 300000 500000 1000000 2000000 5000000; do \
    		echo "Running tests for size = $$size"; \
    		ARRAY_SIZE=$$size pytest src/performance_sandbox_test.py --color=yes -p no:warnings --disable-warnings --benchmark-sort=max --benchmark-disable-gc --benchmark-columns=min,max,mean,stddev,ops --benchmark-min-rounds=35 --benchmark-save=$${timestamp}_sandbox_$${size}; \
    	done
.PHONY: benchmarks_arm

benchmarks_x86:
	@timestamp=$$(date +%Y%m%d_%H%M%S) && \
    	for size in 20000 30000 50000 100000 150000 200000 300000 500000 1000000 2000000 5000000; do \
    		echo "Running tests for size = $$size"; \
    		ARRAY_SIZE=$$size pytest src/performance_enterprise_test.py --color=yes -p no:warnings --disable-warnings --benchmark-sort=max --benchmark-disable-gc --benchmark-columns=min,max,mean,stddev,ops --benchmark-min-rounds=35 --benchmark-save=$${timestamp}_enterprise_$${size}; \
    	done
.PHONY: benchmarks_x86

plot:
	@LAST_TEST_ID=$$(find .benchmarks/$$BENCHMARKS_PLATFORM -name '*.json' | sort | tail -n 1 | sed -E 's#.*/([0-9]+)_.*#\1#'); \
    	echo "Benchmarks with LAST_TEST_ID=$$LAST_TEST_ID are plotting..."; \
    	python -m src.performance_plots $$LAST_TEST_ID $$BENCHMARKS_PLATFORM
.PHONY: plot


test_arm: benchmarks_arm plot
	echo "Purem Benchmarks successfully validated various performance."
.PHONY: test_arm


test_x86: benchmarks_x86 plot
	echo "Purem Benchmarks successfully validated various performance."
.PHONY: test_x86


ec2_ssh_key:
	aws ec2 create-key-pair --key-name $(EC2_SSH_KEY_NAME) --query "KeyMaterial" --output text > $(EC2_SSH_KEY_NAME).pem
	chmod 600 $(EC2_SSH_KEY_NAME).pem
.PHONY: ec2_ssh_key

github_ssh_key:
	ssh-keygen -t rsa -b 4096 -C "ec2_repo_key" -f ec2_repo_key
.PHONY: github_ssh_key

launch_ec2_instance:
	(aws ec2 run-instances \
		--image-id "$(AMI_ID)" \
		--count 1 \
		--instance-type "$(INSTANCE_TYPE)" \
		--key-name "$(AWS_KEY_NAME)" \
		--security-group-ids "$(AWS_SECURITY_GROUP)" \
		--subnet-id "$(AWS_SUBNET_ID)" \
		--block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":32}}]' \
		--query "Instances[0].InstanceId" \
		--output text) || { echo "Error: Failed to create EC2 instance."; exit 1; }
.PHONY: launch_ec2_instance

# Retrieve PUBLIC EC2 INSTANCE IP at first
copy_ssh_key:
	# Copy target repo to EC2
	scp -r -o StrictHostKeyChecking=no -i $(AWS_KEY_NAME).pem . ubuntu@$(INSTANCE_IP):~/
.PHONY: copy_ssh_key


init_python_env:
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt
.PHONY: init_python_env


install_ec2_instance: launch_ec2_instance
	@echo "EC2 Instance launched, AMI ID: $(AMI_ID)"
.PHONY: install_ec2_instance






