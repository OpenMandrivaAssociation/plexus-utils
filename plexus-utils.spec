# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# If you want to build with maven,
# give rpmbuild option '--with maven'

%define with_maven %{!?_with_maven:0}%{?_with_maven:1}
%define without_maven %{?_with_maven:0}%{!?_with_maven:1}
%define gcj_support 1

Name:           plexus-utils
Version:        1.2
Release:        %mkrel 2.1.2
Epoch:          0
Summary:        Plexus Common Utilities
License:        Apache License
Group:          Development/Java
URL:            http://plexus.codehaus.org/
# svn export svn://svn.plexus.codehaus.org/plexus/tags/plexus-utils-1.2/
# tar xzf plexus-utils-1.2.tar.gz plexus-utils-1.2
Source0:        plexus-utils-1.2.tar.gz
Source1:        plexus-utils-1.2-build.xml
# build it with maven2-generated ant build.xml
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
BuildRequires:  java-devel
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires:  ant
BuildRequires:  jpackage-utils >= 0:1.6
Requires:       jpackage-utils
Requires(postun): jpackage-utils
%if %{with_maven}
BuildRequires:  maven2
%endif

%description
The Plexus project seeks to create end-to-end developer tools for 
writing applications. At the core is the container, which can be 
embedded or for a full scale application server. There are many 
reusable components for hibernate, form processing, jndi, i18n, 
velocity, etc. Plexus also includes an application server which 
is like a J2EE application server, without all the baggage.

%package javadoc
Summary:          Javadoc for %{name}
Group:            Development/Java
Requires:         jpackage-utils
Requires(postun): jpackage-utils

%description javadoc
Javadoc for %{name}.


%prep
%setup -q -n plexus-utils-1.2
cp %{SOURCE1} build.xml

# Disable file utils test cases. See:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=228419
rm -f src/test/java/org/codehaus/plexus/util/FileUtilsTest.java

# TODO: Find out why this test keeps freezing
rm -f src/test/java/org/codehaus/plexus/util/interpolation/RegexBasedInterpolatorTest.java

%build
%if %{with_maven}
mkdir -p .maven/repository/maven/jars
build-jar-repository .maven/repository/maven/jars \
maven-jelly-tags

export MAVEN_HOME_LOCAL=$(pwd)/.maven
maven \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=$MAVEN_HOME_LOCAL \
        jar:install javadoc 

%else
%{ant} jar javadoc
%endif

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/plexus
install -pm 644 target/%{name}-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/plexus/utils-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir}/plexus && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr target/docs/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root,-)
%{_javadir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}
