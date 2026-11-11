Name:		plexus-utils
Version:	3.6.2
Release:	2
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
# Gradle 9.9.1 strictly pins 3.6.1. No prebuilt jars.
Source1:	https://github.com/codehaus-plexus/plexus-utils/archive/refs/tags/plexus-utils-3.6.1.tar.gz#/plexus-utils-3.6.1.tar.gz
BuildArch:	noarch
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	plexus-pom >= 27
BuildRequires:	mvn(org.codehaus.plexus:plexus:pom::)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
Utility classes shared by Plexus components: strings, files, command
lines, XML, and related helpers. 3.6.2 is the current 3.x release and
still ships Xpp3Dom and CachingOutputStream. Those classes left the
jar in 4.x.

3.6.1 checks archive entry paths with canonical paths before
extraction, and directory scans no longer exclude **/.cvsignore by
default. The jar manifest names the automatic module
org.codehaus.plexus.util. 3.6.2 itself moves the parent POM to
plexus 27. 3.6.2 stays the default jar. Gradle 9.9.1 strictly
pins 3.6.1, so that jar is installed beside it.

%prep
%autosetup -n plexus-utils-plexus-utils-%{version}
%setup -q -T -D -a 1 -n plexus-utils-plexus-utils-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build -a
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
mkdir -p pu361/classes
find plexus-utils-plexus-utils-3.6.1/src/main/java -name '*.java' ! -name 'module-info.java' > pu361/sources.list
test -s pu361/sources.list
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-d pu361/classes @pu361/sources.list
"$JAVA_HOME/bin/jar" cf pu361/plexus-utils.jar -C pu361/classes .
cat > pu361/plexus-utils.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.codehaus.plexus</groupId>
  <artifactId>plexus-utils</artifactId>
  <version>3.6.1</version>
  <name>Plexus Common Utilities</name>
  <description>Utility classes shared by Plexus components.</description>
  <url>https://codehaus-plexus.github.io/plexus-utils/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
</project>
EOF

%install -p
sysjar install --buildroot %{buildroot} \
	--artifact pu361/plexus-utils.pom:pu361/plexus-utils.jar \
	--file-name plexus-utils-3.6.1 \
	--filelist .mfiles361
# 3.6.2 owns plexus-utils.sysjar. 3.6.1 keeps a second index.
/bin/mv %{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils.sysjar \
	%{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils-3.6.1.sysjar
sed -i 's|/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils\.sysjar|/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils-3.6.1.sysjar|' .mfiles361

%install -a
while IFS= read -r line; do
	grep -qxF -- "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles361

%check -a
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
cat > PuSmoke.java << 'EOF'
import org.codehaus.plexus.util.StringUtils;
public class PuSmoke {
	public static void main(String[] args) {
		String out = StringUtils.join(new String[] {"a", "b"}, ",");
		if (!"a,b".equals(out)) {
			throw new AssertionError(out);
		}
		System.out.println(args[0] + " " + out);
	}
}
EOF
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{buildroot}%{_javadir}/plexus-utils.jar PuSmoke.java
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/plexus-utils.jar:." PuSmoke pu362_ok > check362.log
cat check362.log
grep -F -q 'pu362_ok a,b' check362.log
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{buildroot}%{_javadir}/plexus-utils-3.6.1.jar PuSmoke.java
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/plexus-utils-3.6.1.jar:." PuSmoke pu361_ok > check361.log
cat check361.log
grep -F -q 'pu361_ok a,b' check361.log

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt README.md
