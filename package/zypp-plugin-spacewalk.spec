Name:    zypp-plugin-spacewalk
Version: 0.2
Release: 0
Group:	 System Environment/Base
License: GPLv2
Summary: Client side Spacewalk integration for ZYpp
Source0: zypp-plugin-spacewalk.tar.bz2
# Actually needs just libzypp, but we also want zypper to
# handle services correctly:
%if 0%{?suse_version} == 1110 || 0%{?suse_version} == 1010
# on SLES11-SP1
# on SLES10-SP3
BuildRequires: libzypp >= 6.35.0
Requires: zypper >= 1.3.12
%else
# since 11.4
BuildRequires: libzypp >= 8.12.0
Requires: zypper >= 1.5.3
%endif
Requires: python-xml

# NOTE: zypp-plugin-python should become a seaparte package
# one day. By now we provide the name and install the plugin
# module in %{py_sitedir} too.
Requires:	python
BuildRequires:	python-devel
Provides:	zypp-plugin-python = %{version}

Requires: rhn-client-tools >= 1.1.15
Provides: zypp-service-plugin(spacewalk) = %{version}
Provides: zypp-media-plugin(spacewalk) = %{version}
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
This plugin allows a ZYpp powered Linux system to see Spacewalk
subscribed repositories as well as downloading packages from the
a Spacewalk compatible server.

%prep
%setup -q -n zypp-plugin-spacewalk

%build

%install
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/services
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/system
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver

%{__install} bin/spacewalk-service.py %{buildroot}%{_prefix}/lib/zypp/plugins/services/spacewalk
%{__install} bin/spacewalk-system.py %{buildroot}%{_prefix}/lib/zypp/plugins/system/spacewalk
%{__install} bin/spacewalk-resolver.py %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver/spacewalk

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/python
%{__install} python/zypp/plugins.py %{buildroot}%{_datadir}/%{name}/python

%{__mkdir_p} %{buildroot}%{_datadir}/rhn/actions
%{__install} bin/spacewalk-action-package.py %{buildroot}%{_datadir}/rhn/actions/packages.py

%{__mkdir_p} %{buildroot}%{_var}/lib/up2date

# NOTE: zypp-plugin-python should become a seaparte package
# one day. By now we provide the name and install the plugin
# module in %{py_sitedir} too.
%{__mkdir_p} %{buildroot}%{py_sitedir}
%{__install} python/zypp/plugins.py %{buildroot}%{py_sitedir}/zypp_plugin.py

%files
%defattr(-,root,root)
%dir %{_prefix}/lib/zypp
%dir %{_prefix}/lib/zypp/plugins
%dir %{_prefix}/lib/zypp/plugins/services
     %{_prefix}/lib/zypp/plugins/services/spacewalk
%dir %{_prefix}/lib/zypp/plugins/system
     %{_prefix}/lib/zypp/plugins/system/spacewalk
%dir %{_prefix}/lib/zypp/plugins/urlresolver
     %{_prefix}/lib/zypp/plugins/urlresolver/spacewalk
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/python
     %{_datadir}/%{name}/python/plugins.py
%dir %{_datadir}/rhn
%dir %{_datadir}/rhn/actions
     %{_datadir}/rhn/actions/packages.py
%dir %{_var}/lib/up2date
%{py_sitedir}/zypp_plugin.py