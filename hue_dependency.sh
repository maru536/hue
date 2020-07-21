curl -sL https://rpm.nodesource.com/setup_12.x | sudo -E bash -H
sudo yum install -y ant aAsciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap-devel python-devel sqlite-devel gmp-devel nodejs python-pip
sudo pip install --upgrade pip
pip install -r requirements.txt