#!/bin/bash 

mkdir -p ~/rpmbuild/SOURCES

sudo yum -y install spectool
sudo yum -y install rpm-build
spectool -g -R kong.spec

cp ../SOURCES/kong.lua ~/rpmbuild/SOURCES
cp ../SOURCES/kong.sh ~/rpmbuild/SOURCES
cp ../SOURCES/kong_init.sh ~/rpmbuild/SOURCES
cp ../SOURCES/kong_defaults ~/rpmbuild/SOURCES

rpmbuild -ba kong.spec
echo "sudo rpm -Uvh ~/rpmbuild/RPMS/x86_64/kong-0.13.1-1.el7.centos.x86_64.rpm"
