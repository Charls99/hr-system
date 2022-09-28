# Install flask on EC2 
# Either add "sudo" before all commands or use "sudo su" first

#!/bin/bash
yum update -y
yum install git -y
git clone https://github.com/Charls99/hr-system.git
cd hr-system
pip3 install flask
pip3 install pymysql
pip3 install boto3
python3 EmpApp.py


HeidiSQL
------------
username: hr_user
password hruser123

endpoint: employee.chns3foo4g0p.us-east-1.rds.amazonaws.com

DNS: AssignmentLB-1232896176.us-east-1.elb.amazonaws.com