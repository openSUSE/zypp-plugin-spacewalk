Name:    zypp-plugin-spacewalk
Version: 0.1
Release: 0
Group:	 System Environment/Base
License: Unclear
Summary: Client side Spacewalk integration for ZYpp
Source0: zypp-plugin-spacewalk.tar.bz2
BuildRequires: libzypp => 6.33.4
BuildRequires: rhn-client-tools  >= 1.1.15
BuildRequires: rhn_check
Requires: libzypp >= 6.33.4
Requires: python
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
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver

%{__install} bin/spacewalk-service.py %{buildroot}%{_prefix}/lib/zypp/plugins/services/spacewalk
%{__install} bin/spacewalk-resolver.py %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver/spacewalk

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/python
%{__install} python/zypp/plugins.py %{buildroot}%{_datadir}/%{name}/python

%{__mkdir_p} %{buildroot}%{_datadir}/rhn/actions
%{__install} bin/spacewalk-action-package.py %{buildroot}%{_datadir}/rhn/actions/packages.py

%files
%defattr(-,root,root)
%dir %{_prefix}/lib/zypp
%dir %{_prefix}/lib/zypp/plugins
%dir %{_prefix}/lib/zypp/plugins/services
%dir %{_prefix}/lib/zypp/plugins/urlresolver
%{_datadir}/rhn/actions/packages.py
%{_prefix}/lib/zypp/plugins/services/spacewalk
%{_prefix}/lib/zypp/plugins/urlresolver/spacewalk
%{_datadir}/%{name}/python/plugins.py
