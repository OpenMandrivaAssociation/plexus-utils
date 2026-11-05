Name:		plexus-utils
Version:	3.6.0
Release:	1
Summary:	Plexus Common Utilities
Group:		Development/Java
# ASL 1.1: several files in src/main/java/org/codehaus/plexus/util/
# xpp: src/main/java/org/codehaus/plexus/util/xml/pull
# ASL 2.0 and BSD: StreamConsumer, StreamPumper, Commandline
# Public domain: TypeFormat.java
# The rest is ASL 2.0.
License:	ASL 1.1 and ASL 2.0 and xpp and BSD and Public Domain
URL:		https://codehaus-plexus.github.io/plexus-utils/
Source0:	https://github.com/codehaus-plexus/plexus-utils/archive/refs/tags/plexus-utils-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	plexus-pom
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
Utility classes shared by Plexus components: strings, files, command
lines, XML, and related helpers. 3.6.0 is the last release that still
ships Xpp3Dom and CachingOutputStream. Those classes left the jar in 4.x.

%prep
%autosetup -n plexus-utils-plexus-utils-%{version}

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt README.md
