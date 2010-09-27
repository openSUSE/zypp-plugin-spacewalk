Name:    zypp-plugin-spacewalk
Version: 0.1
Release: 0
License: Unclear
Summary: Client side Spacewalk integration for ZYpp
Source0: zypp-plugin-spacewalk-%{version}.tar.bz2
Requires: 
Provides: zypp-service-plugin(spacewalk) = %{version}
Provides: zypp-media-plugin(spacewalk) = %{version}

%description
This plugin allows a ZYpp powered Linux system to see Spacewalk
subscribed repositories as well as downloading packages from the
a Spacewalk compatible server.

%prep

%setup -q -n %{name}

%build

%install
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/services
%{__install} bin/spacewalk-service.py %{buildroot}%{_prefix}/lib/zypp/plugins/services/spacewalk

%files
%defattr(-,root,root)
%{_prefix}/lib/zypp/plugins/services/spacewalk