#
# spec file for package zypp-plugin-spacewalk
#
# Copyright (c) 2015 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           zypp-plugin-spacewalk
Version:        0.9.10
Release:        0
Summary:        Client side Spacewalk integration for ZYpp
License:        GPL-2.0
Group:          System Environment/Base
Source0:        zypp-plugin-spacewalk.tar.bz2
Source1:        zypp-plugin-spacewalk-rpmlintrc
# Actually needs just libzypp, but we also want zypper to
# handle services correctly:
%if 0%{?suse_version} == 1010
# on SLES10 require basic code10->11 metadata conversion tools
Requires:       libzypp(code10)
# esp. for OES we need to provide zmd as it's required by the
# products -release package. :(
Provides:       zmd <= 7.3.0.0
%endif
%if 0%{?suse_version} == 1110 || 0%{?suse_version} == 1010
# on SLES11-SP1
# on SLES10-SP3
BuildRequires:  libzypp >= 6.35.0
Requires:       zypper >= 1.3.12
%else
# since 11.4
BuildRequires:  libzypp >= 8.12.0
Requires:       zypper >= 1.5.3
%endif
%if 0%{?suse_version} >= 1315
# SLES12+
Requires:       zypper(updatestack-only)
%endif

Requires:       python-xml

Requires:       python
BuildRequires:  python-devel
Requires:       zypp-plugin-python

Requires:       rhn-client-tools >= 1.7.7
Requires:       zypper(oldpackage)
Provides:       zypp-media-plugin(spacewalk) = %{version}
Provides:       zypp-service-plugin(spacewalk) = %{version}
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
This plugin allows a ZYpp powered Linux system to see Spacewalk
subscribed repositories as well as downloading packages from the
a Spacewalk compatible server.

%prep
%setup -q -n zypp-plugin-spacewalk

%build
grep -E -r -l "\#\!\s*/usr/bin/env\s+python" * | xargs -i -d "\n" sed -i -e"s:\#\![ \t]*/usr/bin/env[ \t]\+python:\#\!/usr/bin/python:" {}

%install
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/services
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/system
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/

%{__install} bin/spacewalk-service.py %{buildroot}%{_prefix}/lib/zypp/plugins/services/spacewalk
%{__install} bin/spacewalk-system.py %{buildroot}%{_prefix}/lib/zypp/plugins/system/spacewalk
%{__install} bin/spacewalk-resolver.py %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver/spacewalk

%{__mkdir_p} %{buildroot}%{_datadir}/rhn/actions
%{__install} actions/packages.py %{buildroot}%{_datadir}/rhn/actions/
%{__install} actions/errata.py %{buildroot}%{_datadir}/rhn/actions/
%{__install} actions/distupgrade.py %{buildroot}%{_datadir}/rhn/actions/

%{__install} -m 0644 clientCaps/packages %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/
%if 0%{?suse_version} >= 1315
%{__install} -m 0644 clientCaps/distupgrade2 %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/distupgrade
%else
%{__install} -m 0644 clientCaps/distupgrade %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/
%endif

%{__mkdir_p} %{buildroot}%{_var}/lib/up2date

%if 0%{?suse_version}
%py_compile %{buildroot}%{_datadir}/rhn/actions
%endif

%files
%defattr(-,root,root)
%doc COPYING
%dir %{_prefix}/lib/zypp
%dir %{_prefix}/lib/zypp/plugins
%dir %{_prefix}/lib/zypp/plugins/services
     %{_prefix}/lib/zypp/plugins/services/spacewalk
%dir %{_prefix}/lib/zypp/plugins/system
     %{_prefix}/lib/zypp/plugins/system/spacewalk
%dir %{_prefix}/lib/zypp/plugins/urlresolver
     %{_prefix}/lib/zypp/plugins/urlresolver/spacewalk
%dir %{_datadir}/rhn
%dir %{_datadir}/rhn/actions
     %{_datadir}/rhn/actions/packages.py*
     %{_datadir}/rhn/actions/errata.py*
     %{_datadir}/rhn/actions/distupgrade.py*
%dir %{_var}/lib/up2date
%dir %{_sysconfdir}/sysconfig/rhn
%dir %{_sysconfdir}/sysconfig/rhn/clientCaps.d
%config %{_sysconfdir}/sysconfig/rhn/clientCaps.d/packages
%config %{_sysconfdir}/sysconfig/rhn/clientCaps.d/distupgrade

%changelog
