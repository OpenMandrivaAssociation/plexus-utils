# Copyright (c) 2000-2007, JPackage Project
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

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven 0
%define gcj_support 1

%define parent plexus
%define subname utils


Summary:	Plexus Common Utilities
Name:		plexus-utils
Version:	1.4.8
Release:	1.0.6
License:	Apache License
Group:		Development/Java
Url:		http://plexus.codehaus.org/
# svn export svn://svn.plexus.codehaus.org/plexus/tags/plexus-utils-1.8/
# tar xzf plexus-utils-1.8.tar.gz plexus-utils-1.8
Source0:	plexus-utils-1.4.8.tar.gz
Source1:	plexus-utils-1.4.8-build.xml
# build it with maven2-generated ant build.xml
%if !%{gcj_support}
BuildArch:	noarch
BuildRequires:	java-devel
%else
BuildRequires:	java-gcj-compat-devel
%endif
BuildRequires:	ant >= 0:1.6.5
BuildRequires:	locales-en
BuildRequires:	java-rpmbuild >= 0:1.6
%if %{with_maven}
BuildRequires:	maven2 >= 0:2.0.4
BuildRequires:	maven2-plugin-surefire
BuildRequires:	maven2-plugin-resources
BuildRequires:	maven2-plugin-compiler
BuildRequires:	maven2-plugin-jar
BuildRequires:	maven2-plugin-install
BuildRequires:	maven2-plugin-release
BuildRequires:	maven2-plugin-javadoc
%endif
Requires:	jpackage-utils
Requires(postun):	jpackage-utils

%description
The Plexus project seeks to create end-to-end developer tools for 
writing applications. At the core is the container, which can be 
embedded or for a full scale application server. There are many 
reusable components for hibernate, form processing, jndi, i18n, 
velocity, etc. Plexus also includes an application server which 
is like a J2EE application server, without all the baggage.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java
Requires:	jpackage-utils
Requires(postun):	jpackage-utils

%description javadoc
Javadoc for %{name}.

%prep
%setup -q
cp %{SOURCE1} build.xml

%build
export LC_ALL=ISO-8859-1
%if %{with_maven}
export MAVEN_REPO_LOCAL=`pwd`/.m2/repository

mvn-jpp -e \
    -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
    install javadoc:javadoc


%else
export CLASSPATH=target/classes:target/test-classes
%{ant} -Dbuild.sysclasspath=only jar javadoc
%endif

%install
# jars
install -d -m 755 %{buildroot}%{_javadir}/plexus
install -pm 644 target/%{name}-%{version}.jar \
  %{buildroot}%{_javadir}/plexus/utils-%{version}.jar
%add_to_maven_depmap org.codehaus.plexus %{name} %{version} JPP/%{parent} %{subname}
(cd %{buildroot}%{_javadir}/plexus && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# pom
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 pom.xml %{buildroot}%{_datadir}/maven2/poms/JPP.%{parent}-%{subname}.pom

# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%{_javadir}/*
%{_datadir}/maven2
%config(noreplace) %{_mavendepmapfragdir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

