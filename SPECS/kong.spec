Name:           kong
Version:        0.13.1 
Release:        1%{?dist}
Summary:        Kong API Gateway

Group:          Development/System
License:        APL
URL:            https://getkong.org/
Source0:        https://github.com/kong/kong/archive/0.13.1.tar.gz
Source1:        https://openresty.org/download/openresty-1.11.2.5.tar.gz
Source2:        https://github.com/luarocks/luarocks/archive/2.4.3.tar.gz
Source3:        kong_init.sh
Source4:        kong.sh
Source5:        kong.lua
Source6:        kong_defaults

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires(pre): /usr/sbin/useradd, /usr/bin/getent, chkconfig
Requires(postun): /usr/sbin/userdel, chkconfig

%global debug_package %{nil}
%define rockfile kong-0.13.1-0

%define prefix /usr/local
%define orprefix %{prefix}/openresty
%define luajit %{orprefix}/luajit
%define target /usr/local/kong
%define luarocks %{buildroot}%{luajit}/bin/luajit %{buildroot}%{prefix}/bin/luarocks
%define luarocksdir /usr/local/share/lua/5.1/luarocks


%description
This package contains the Kong API Gateway

# ### ### ### ###
# Prep
# ### ### ### ###

%define user kong

%pre
# /usr/bin/getent group %{user} || /usr/sbin/groupadd -r %{user}
/usr/bin/getent passwd %{user} || /usr/sbin/useradd -r -d /usr/local/kong %{user}

%post
/sbin/chkconfig --add %{name}

%postun
/usr/sbin/userdel %{user}

%preun
if [ $1 = 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%prep
%setup -c -q -n %{name}-%{version} -T -a0 -a1 -a2 

# ### ### ### ###
# Build
# ### ### ### ###

%build

# ### ### ### ###
##  pt1 - Executable
# ### ### ### ###

# Build openresty
cd openresty-1.11.2.5
./configure \
  --prefix="%{orprefix}" \
  --with-pcre-jit \
  --with-ipv6 \
  --with-http_realip_module \
  --with-http_ssl_module \
  --with-http_stub_status_module \
  --with-http_v2_module 

gmake 
gmake install DESTDIR=%{buildroot}

echo "%{luajit}"
echo "%{buildroot}%{luajit}"

cd ../luarocks-2.4.3
./configure \
  --prefix="%{buildroot}%{prefix}" \
  --lua-suffix=jit \
  --sysconfdir="%{buildroot}/usr/local/etc/luarocks" \
  --with-lua="%{buildroot}%{luajit}" \
  --with-lua-include="%{buildroot}%{luajit}/include/luajit-2.1" \
  --force-config
make build
make install 

export PATH="%{buildroot}:$PATH"
echo $PATH
# Needed to change the location of the package for it to work
# need to figure out how to solve that later

cd ../kong-%{version}
%{luarocks} pack %{rockfile}.rockspec --tree %{buildroot}%{target}

# ### ### ### ###
## pt2 - Documentation
# ### ### ### ###

# Builds HTML documentation
# make luadoc

# ### ### ### ###
# Install
# ### ### ### ###

%install

%{__mkdir} -p %{buildroot}/%{_bindir}
%{__mkdir} -p %{buildroot}/%{target}
%{__mkdir} -p %{buildroot}/etc/init.d
%{__mkdir} -p %{buildroot}/etc/sysconfig
cp %{SOURCE3} %{buildroot}/etc/init.d/kong
cp %{SOURCE4} %{buildroot}/%{_bindir}/kong
cp %{SOURCE5} %{buildroot}/%{target}/kong.lua
cp %{SOURCE6} %{buildroot}/etc/sysconfig/kong

cd openresty-1.11.2.5
make install DESTDIR=%{buildroot}
cd ../luarocks-2.4.3
make install 
%{luarocks} install --server=https://artifactory.eng.fireeye.com/HX-Build-Deps/luarocks/ %{_builddir}/%{name}-%{version}/%{name}-%{version}/%{rockfile}.src.rock --tree %{buildroot}%{target}
cat /home/devuser/rpmbuild/BUILDROOT/kong-0.13.1-1.el7.centos.x86_64/usr/local/kong/bin/lapis

for i in %{buildroot}%{target}/bin/*; do
  sed -i 's+%{buildroot}++' $i
done
for i in %{buildroot}%{target}/bin/*; do
  sed -i 's:%{buildroot}::g' $i
done
for i in %{buildroot}%{luajit}/bin/*; do
  sed -i 's:%{buildroot}::g' $i
done

for i in %{buildroot}/usr/local/bin/*; do
  sed -i 's:%{buildroot}::g' $i
done
sed -i 's:%{buildroot}::g' %{buildroot}%{prefix}/share/lua/5.1/luarocks/site_config.lua
sed -i 's:%{buildroot}::g' %{buildroot}/usr/local/etc/luarocks/config-5.1.lua

# ### ### ### ###
# Clean
# ### ### ### ###

%clean
rm -rf %{buildroot}

# ### ### ### ###
# Files
# ### ### ### ###

%files
%{orprefix}
%{target}
/usr/local/bin/luarocks
/usr/local/bin/luarocks-5.1
/usr/local/bin/luarocks-admin
/usr/local/bin/luarocks-admin-5.1
/usr/local/etc/luarocks/config-5.1.lua
/usr/local/share/lua/5.1/luarocks
%attr(755, root, root) %{_bindir}/kong
%attr(755, %{user}, %{user}) %{target}/kong.lua
%attr(755, root, root) /etc/init.d/kong
%config(noreplace) /etc/sysconfig/kong

%changelog
* Tue Feb 14 2017 Chris Heald
- Initial packaging
