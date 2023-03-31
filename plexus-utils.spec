%{?_javapackages_macros:%_javapackages_macros}
%global parent plexus
%global subname utils

Name:           plexus-utils
Version:	3.2.1
Release:	2
Summary:        Plexus Common Utilities
Group:		Development/Java
# ASL 1.1: several files in src/main/java/org/codehaus/plexus/util/ 
# xpp: src/main/java/org/codehaus/plexus/util/xml/pull directory
# ASL 2.0 and BSD:
#      src/main/java/org/codehaus/plexus/util/cli/StreamConsumer
#      src/main/java/org/codehaus/plexus/util/cli/StreamPumper
#      src/main/java/org/codehaus/plexus/util/cli/Commandline            
# Public domain: src/main/java/org/codehaus/plexus/util/TypeFormat.java
# rest is ASL 2.0
License:        ASL 1.1 and ASL 2.0 and xpp and BSD and Public Domain
URL:            https://codehaus-plexus.github.io/plexus-utils/
Source0:        https://github.com/codehaus-plexus/%{name}/archive/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  jdk-current
BuildRequires:	javapackages-local

%description
The Plexus project seeks to create end-to-end developer tools for
writing applications. At the core is the container, which can be
embedded or for a full scale application server. There are many
reusable components for hibernate, form processing, jndi, i18n,
velocity, etc. Plexus also includes an application server which
is like a J2EE application server, without all the baggage.

%package javadoc
Summary:          Javadoc for %{name}

%description javadoc
Javadoc for %{name}.

%prep
%setup -n %{name}-%{name}-%{version}
# Fix up javadoc snippets
find . -name "*.java" |xargs sed -i -e 's,<tt>,<code>,g;s,</tt>,</code>,g'

mv pom.xml org.codehaus.plexus.util-%{version}.pom

# Add module information
cd src/main/java
cat >module-info.java <<'EOF'
module org.codehaus.plexus.util {
	exports org.codehaus.plexus.util;
	exports org.codehaus.plexus.util.cli;
	exports org.codehaus.plexus.util.cli.shell;
	exports org.codehaus.plexus.util.dag;
	exports org.codehaus.plexus.util.introspection;
	exports org.codehaus.plexus.util.io;
	exports org.codehaus.plexus.util.reflection;
	exports org.codehaus.plexus.util.xml;
	exports org.codehaus.plexus.util.xml.pull;
	requires java.sql;
}
EOF

%build
. %{_sysconfdir}/profile.d/90java.sh
export PATH=$JAVA_HOME/bin:$PATH
cd src/main/java
find . -name "*.java" |xargs javac -d ../resources
javadoc -d ../javadoc org.codehaus.plexus.util
cd ../resources
jar cf ../org.codehaus.plexus.util-%{version}.jar *
jar i ../org.codehaus.plexus.util-%{version}.jar

%install
mkdir -p %{buildroot}%{_javadir}/modules %{buildroot}%{_javadocdir} %{buildroot}%{_mavenpomdir}
cp *.pom %{buildroot}%{_mavenpomdir}/
cp src/main/org.codehaus.plexus.util-%{version}.jar %{buildroot}%{_javadir}/modules/
ln -s modules/org.codehaus.plexus.util-%{version}.jar %{buildroot}%{_javadir}/
ln -s modules/org.codehaus.plexus.util-%{version}.jar %{buildroot}%{_javadir}/org.codehaus.plexus.util.jar
cp -a src/main/javadoc %{buildroot}%{_javadocdir}/%{name}
%add_maven_depmap org.codehaus.plexus.util-%{version}.pom org.codehaus.plexus.util-%{version}.jar

%files -f .mfiles
%{_javadir}/modules/*.jar
%{_javadir}/*.jar

%files javadoc
%{_javadocdir}/%{name}
