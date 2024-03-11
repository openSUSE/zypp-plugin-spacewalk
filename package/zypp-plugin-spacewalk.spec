#
# spec file for package zypp-plugin-spacewalk
#
# Copyright (c) 2023 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%{!?python2_sitelib: %global python2_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%if 0%{?suse_version} > 1320 || 0%{?rhel} >= 8
%bcond_without python3
%else
%bcond_with python3
%endif

Name:           zypp-plugin-spacewalk
Version:        1.0.15
Release:        0
Summary:        Client side Spacewalk integration for ZYpp
License:        GPL-2.0-only
Group:          System Environment/Base
URL:            https://github.com/openSUSE/zypp-plugin-spacewalk
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
%if 0%{?sle_version} >= 120000
# SLES12+
Requires:       zypper(updatestack-only)
%endif
Requires:       zypper(oldpackage)

%if %{without python3}
Requires:       python
Requires:       python-xml
Requires:       rhn-client-tools >= 1.7.7
Requires:       rhnlib
Requires:       zypp-plugin-python
BuildRequires:  python-devel
%else
Requires:       python3
Requires:       python3-rhnlib
Requires:       python3-zypp-plugin
Requires:       rhn-client-tools >= 2.8.4
BuildRequires:  python3-devel
BuildRequires:  python3-rpm-macros
%endif

Provides:       zypp-media-plugin(spacewalk) = %{version}
Provides:       zypp-service-plugin(spacewalk) = %{version}
%if 0%{?suse_version} >= 1210
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
This plugin allows a ZYpp powered Linux system to see Spacewalk
subscribed repositories as well as downloading packages from the
a Spacewalk compatible server.

%prep
%setup -q -n zypp-plugin-spacewalk

%build
%if %{with python3}
grep -E -r -l "\#\!\s*/usr/bin/env\s+python" * | xargs -i -d "\n" sed -i -e"s:\#\![ \t]*/usr/bin/env[ \t]\+python:\#\!/usr/bin/python3:" {}
%else
grep -E -r -l "\#\!\s*/usr/bin/env\s+python" * | xargs -i -d "\n" sed -i -e"s:\#\![ \t]*/usr/bin/env[ \t]\+python:\#\!/usr/bin/python:" {}
%endif

%install
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/services
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/system
%{__mkdir_p} %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/

%{__install} bin/spacewalk-service.py %{buildroot}%{_prefix}/lib/zypp/plugins/services/spacewalk
%{__install} bin/spacewalk-system.py %{buildroot}%{_prefix}/lib/zypp/plugins/system/spacewalk
%{__install} bin/spacewalk-resolver.py %{buildroot}%{_prefix}/lib/zypp/plugins/urlresolver/spacewalk

%{__install} -m 0644 clientCaps/packages %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/
%if 0%{?sle_version} >= 120000
%{__install} -m 0644 clientCaps/distupgrade2 %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/distupgrade
%else
%{__install} -m 0644 clientCaps/distupgrade %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/
%endif

%{__mkdir_p} %{buildroot}%{_var}/lib/up2date

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
%dir %{_var}/lib/up2date
%dir %{_sysconfdir}/sysconfig/rhn
%dir %{_sysconfdir}/sysconfig/rhn/clientCaps.d
%config %{_sysconfdir}/sysconfig/rhn/clientCaps.d/packages
%config %{_sysconfdir}/sysconfig/rhn/clientCaps.d/distupgrade

%changelog
