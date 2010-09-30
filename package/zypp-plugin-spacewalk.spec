Name:    zypp-plugin-spacewalk
Version: 0.1
Release: 0
License: Unclear
Summary: Client side Spacewalk integration for ZYpp
Source0: zypp-plugin-spacewalk.tar.bz2
Requires: python
Requires: rhn-client-tools >= 1.1.15
Provides: zypp-service-plugin(spacewalk) = %{version}
Provides: zypp-media-plugin(spacewalk) = %{version}

%description
This plugin allows a ZYpp powered Linux system to see Spacewalk
subscribed repositories as well as downloading packages from the
a Spacewalk compatible server.

%prep

%setup -q -n zypp-plugin-spacewalk

%build

%install
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/services
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/resolver

%{__install} bin/spacewalk-service.py %{buildroot}%{_prefix}/lib/zypp/plugins/services/spacewalk
%{__install} bin/spacewalk-resolver.py %{buildroot}%{_prefix}/lib/zypp/plugins/resolver/spacewalk

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/python
%{__install} python/zypp/plugins.py %{buildroot}%{_datadir}/%{name}/python

%files
%defattr(-,root,root)
%dir %{_prefix}/lib/zypp
%dir %{_prefix}/lib/zypp/plugins
%dir %{_prefix}/lib/zypp/plugins/services
%dir %{_prefix}/lib/zypp/plugins/resolver
%{_prefix}/lib/zypp/plugins/services/spacewalk
%{_prefix}/lib/zypp/plugins/resolver/spacewalk
%{_datadir}/%{name}/python/plugins.py
