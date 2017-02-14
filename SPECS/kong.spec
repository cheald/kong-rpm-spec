Name:           kong
Version:        0e7c8f3840d0bc6461584ff8dee1d75402ab9989
Release:        1%{?dist}
Summary:        Kong API Gateway

Group:          Development/System
License:        APL
URL:            https://getkong.org/
Source0:        https://codeload.github.com/Mashape/kong/zip/%{version}
Source1:        https://releases.hashicorp.com/serf/0.8.0/serf_0.8.0_linux_amd64.zip
Source2:        https://openresty.org/download/openresty-1.11.2.2.tar.gz
Source3:        https://github.com/luarocks/luarocks/archive/v2.4.2.tar.gz
Source4:        kong_init.sh
Source5:        kong.sh
Source6:        kong.lua
Source7:        kong_defaults

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch0:         kong-patch-spec.patch

Requires(pre): /usr/sbin/useradd, /usr/bin/getent, chkconfig
Requires(postun): /usr/sbin/userdel, chkconfig, initscripts

%global debug_package %{nil}
%define rockfile kong-0.10.0rc3-0

%define prefix /usr/local
%define orprefix %{prefix}/openresty
%define luajit %{orprefix}/luajit
%define target /usr/local/kong
%define luarocks %{buildroot}/%{luajit}/bin/luajit %{buildroot}/%{luajit}/bin/luarocks

%description
This package contains the Kong API Gateway

# ### ### ### ###
# Prep
# ### ### ### ###

%define user kong

%pre
/usr/bin/getent group %{user} || /usr/sbin/groupadd -r %{user}
/usr/bin/getent passwd %{user} || /usr/sbin/useradd -r -d /usr/bin/kong -s /sbin/nologin %{user}

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
%setup -c -q -n %{name}-%{version} -T -a0 -a1 -a2 -a3

# ### ### ### ###
# Build
# ### ### ### ###

%patch -P 0 -p0

%build

# ### ### ### ###
##  pt1 - Executable
# ### ### ### ###

# Build openresty
cd openresty-1.11.2.2
./configure \
  --prefix="%{orprefix}" \
  --with-pcre-jit \
	--without-http_rds_json_module \
	--without-http_rds_csv_module \
	--without-lua_rds_parser \
	--with-ipv6 \
	--with-stream \
	--with-stream_ssl_module \
	--with-http_v2_module \
	--without-mail_pop3_module \
	--without-mail_imap_module \
	--without-mail_smtp_module \
	--with-http_stub_status_module \
	--with-http_realip_module \
	--with-http_addition_module \
	--with-http_auth_request_module \
	--with-http_secure_link_module \
	--with-http_random_index_module \
	--with-http_geoip_module \
	--with-http_gzip_static_module \
	--with-http_sub_module \
	--with-http_dav_module \
	--with-http_flv_module \
	--with-http_mp4_module \
	--with-http_gunzip_module \
	--with-threads \
	--without-luajit-lua52 \
	--with-file-aio \
	--with-luajit-xcflags='-DLUAJIT_NUMMODE=2' \
	--with-dtrace-probes \
  %{?_smp_mflags}

make %{?_smp_mflags}
make install DESTDIR=%{buildroot}

cd ../luarocks-2.4.2
./configure \
  --prefix="%{luajit}" \
  --sysconfdir="%{orprefix}/luarocks" \
  --lua-suffix=jit \
  --with-lua="%{buildroot}%{luajit}" \
  --with-lua-include="%{luajit}/include/luajit-2.1" \
  --force-config
make
make install DESTDIR=%{buildroot}

cd ../kong-%{version}
%{luarocks} pack %{rockfile}.rockspec --tree %{buildroot}%{target}

# Can't use configure macro here since configure script fails with unsupported
# options

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
cp serf %{buildroot}/%{_bindir}
cp %{SOURCE4} %{buildroot}/etc/init.d/kong
cp %{SOURCE5} %{buildroot}/%{_bindir}/kong
cp %{SOURCE6} %{buildroot}/%{target}/kong.lua
cp %{SOURCE7} %{buildroot}/etc/sysconfig/kong

cd openresty-1.11.2.2
make install DESTDIR=%{buildroot}
cd ../luarocks-2.4.2
make install DESTDIR=%{buildroot}
%{luarocks} install %{_builddir}/%{name}-%{version}/%{name}-%{version}/%{rockfile}.src.rock --tree %{buildroot}%{target}
# rm %{buildroot}/kong-0.10.0rc3-0.src.rock
for i in %{buildroot}%{target}/bin/*; do
  sed -i 's+%{buildroot}++' $i
done

sed -i 's+%{buildroot}++' %{buildroot}%{luajit}/share/lua/5.1/luarocks/site_config.lua

# ### ### ### ###
# Clean
# ### ### ### ###

%clean
rm -rf %{buildroot}

# ### ### ### ###
# Files
# ### ### ### ###

%files
%{target}
%{orprefix}
%attr(755, root, root) %{_bindir}/serf
%attr(755, root, root) %{_bindir}/kong
%attr(755, %{user}, %{user}) %{target}/kong.lua
%attr(755, root, root) /etc/init.d/kong
/etc/sysconfig/kong

%changelog
* Tue Feb 14 2017 Chris Heald
- Initial packaging
