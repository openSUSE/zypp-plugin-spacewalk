#
# spec file for package zypp-plugin-spacewalk
#
# Copyright (c) 2017 SUSE LINUX GmbH, Nuernberg, Germany.
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


%{!?python2_sitelib: %global python2_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%if 0%{?suse_version} > 1320
%bcond_without python3
%bcond_with rhnpath
%global py2_actions %{python2_sitelib}/rhn
%global py3_actions %{python3_sitelib}/rhn
%define pythonX python3
%else
%bcond_with python3
%bcond_with rhnpath
%if %{with rhnpath}
%global py2_actions %{_datadir}/rhn/
%else
%define pythonX python2
%global py2_actions %{python2_sitelib}/rhn
%endif
%endif

Name:           zypp-plugin-spacewalk
Version:        1.0.3
Release:        0
Summary:        Client side Spacewalk integration for ZYpp
License:        GPL-2.0
Group:          System Environment/Base
Url:            https://github.com/openSUSE/zypp-plugin-spacewalk
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
Requires:       zypp-plugin-python
Requires:       rhn-client-tools >= 1.7.7
Requires:       rhnlib
BuildRequires:  python-devel
%else
Requires:       python3
Requires:       python3-zypp-plugin
Requires:       rhn-client-tools >= 2.8.4
Requires:       python3-rhnlib
BuildRequires:  python3-devel
%endif
%if %{without rhnpath}
Requires:       %{pythonX}-%{name} = %{version}-%{release}
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

%if %{without rhnpath}
%package -n python2-%{name}
Summary:        Client side Spacewalk integration for ZYpp
Group:          System Environment/Base
Requires:       %{name} = %{version}-%{release}
Requires:       python2-rhn-client-tools >= 2.8.4
BuildRequires:  python-devel

%description -n python2-%{name}
Python 2 specific files of %{name}
%endif

%if %{with python3}
%package -n python3-%{name}
Summary:        Client side Spacewalk integration for ZYpp
Group:          System Environment/Base
Requires:       %{name} = %{version}-%{release}
BuildRequires:  python3-devel
Requires:       python3
Requires:       python3-rhn-client-tools >= 2.8.4

%description -n python3-%{name}
Python 3 specific files of %{name}
%endif

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

%{__mkdir_p} %{buildroot}%{py2_actions}/actions
%{__install} actions/packages.py %{buildroot}%{py2_actions}/actions/
%{__install} actions/errata.py %{buildroot}%{py2_actions}/actions/
%{__install} actions/distupgrade.py %{buildroot}%{py2_actions}/actions/

%if %{with python3}
%{__mkdir_p} %{buildroot}%{py3_actions}/actions
%{__install} actions/packages.py %{buildroot}%{py3_actions}/actions/
%{__install} actions/errata.py %{buildroot}%{py3_actions}/actions/
%{__install} actions/distupgrade.py %{buildroot}%{py3_actions}/actions/
%endif

%{__install} -m 0644 clientCaps/packages %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/
%if 0%{?sle_version} >= 120000
%{__install} -m 0644 clientCaps/distupgrade2 %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/distupgrade
%else
%{__install} -m 0644 clientCaps/distupgrade %{buildroot}%{_sysconfdir}/sysconfig/rhn/clientCaps.d/
%endif

%{__mkdir_p} %{buildroot}%{_var}/lib/up2date

%if 0%{?suse_version}
%py_compile %{buildroot}%{py2_actions}
%if %{with python3}
%py3_compile %{buildroot}/%{py3_actions}
%endif
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
%if %{with rhnpath}
%dir %{_datadir}/rhn
%dir %{_datadir}/rhn/actions
     %{_datadir}/rhn/actions/packages.py*
     %{_datadir}/rhn/actions/errata.py*
     %{_datadir}/rhn/actions/distupgrade.py*
%endif
%dir %{_var}/lib/up2date
%dir %{_sysconfdir}/sysconfig/rhn
%dir %{_sysconfdir}/sysconfig/rhn/clientCaps.d
%config %{_sysconfdir}/sysconfig/rhn/clientCaps.d/packages
%config %{_sysconfdir}/sysconfig/rhn/clientCaps.d/distupgrade

%if %{without rhnpath}
%files -n python2-%{name}
%defattr(-,root,root)
%dir %{py2_actions}
%dir %{py2_actions}/actions
     %{py2_actions}/actions/packages.py*
     %{py2_actions}/actions/errata.py*
     %{py2_actions}/actions/distupgrade.py*
%endif

%if %{with python3}
%files -n python3-%{name}
%defattr(-,root,root)
%dir %{py3_actions}
%dir %{py3_actions}/actions
%dir %{py3_actions}/actions/__pycache__
     %{py3_actions}/actions/packages.py*
     %{py3_actions}/actions/errata.py*
     %{py3_actions}/actions/distupgrade.py*
     %{py3_actions}/actions/__pycache__/*.py*
%endif

%changelog
