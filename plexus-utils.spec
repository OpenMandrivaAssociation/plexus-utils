Name:		plexus-utils
Version:	4.2.0
Release:	1
Summary:	Plexus Common Utilities
Group:		Development/Java
# The 4.2.0 jar is Apache-2.0. The 3.6.4 and 3.6.1 jars still ship
# the older mix: ASL 1.1 in some util classes, the xpp pull parser,
# BSD on the stream and command classes, and public-domain TypeFormat.
License:	ASL 1.1 and ASL 2.0 and xpp and BSD and Public Domain
URL:		https://codehaus-plexus.github.io/plexus-utils/
Source0:	https://github.com/codehaus-plexus/plexus-utils/archive/refs/tags/plexus-utils-%{version}.tar.gz
# Kept so a classpath can still name the jar that contains Xpp3Dom.
Source1:	https://github.com/codehaus-plexus/plexus-utils/archive/refs/tags/plexus-utils-3.6.4.tar.gz#/plexus-utils-3.6.4.tar.gz
# Gradle 9.9.1 strictly pins 3.6.1. No prebuilt jars.
Source2:	https://github.com/codehaus-plexus/plexus-utils/archive/refs/tags/plexus-utils-3.6.1.tar.gz#/plexus-utils-3.6.1.tar.gz
BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(org.codehaus.plexus:plexus-xml)
%{!?pu_xml:%global pu_xml %{_javadir}/plexus-xml.jar}

%description
Plexus Common Utilities 4.2.0 is the default jar. Xpp3Dom, the pull
parser and the other org.codehaus.plexus.util.xml classes left this
jar in 4.x and live in plexus-xml. ReaderFactory and WriterFactory
still call XmlStreamReader and XmlStreamWriter, so that dependency
stays optional.

sysjar rewrites a request for org.codehaus.plexus:plexus-utils,
including 3.6.4 and 3.6.1, onto 4.2.0. Those two jars stay installed
beside it. Gradle 9.9.1 strictly pins 3.6.1, and code that still
needs Xpp3Dom from this coordinate can name the versioned jar.
The base classes are release 8. Java 9, 10 and 11 overlays ship in
the same multi-release jar. The jar filename keeps the module name
plexus.utils.

%prep
%autosetup -n plexus-utils-plexus-utils-%{version}
%setup -q -T -D -a 1 -n plexus-utils-plexus-utils-%{version}
%setup -q -T -D -a 2 -n plexus-utils-plexus-utils-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete
python - << 'PY'
from pathlib import Path
base = list(Path("src/main/java").rglob("*.java"))
j9 = list(Path("src/main/java9").rglob("*.java"))
j10 = list(Path("src/main/java10").rglob("*.java"))
j11 = list(Path("src/main/java11").rglob("*.java"))
s364 = list(Path("plexus-utils-plexus-utils-3.6.4/src/main/java").rglob("*.java"))
s361 = list(Path("plexus-utils-plexus-utils-3.6.1/src/main/java").rglob("*.java"))
if (len(base), len(j9), len(j10), len(j11), len(s364), len(s361)) != (66, 1, 1, 1, 86, 86):
    raise SystemExit(
        "source count base=" + str(len(base))
        + " j9=" + str(len(j9))
        + " j10=" + str(len(j10))
        + " j11=" + str(len(j11))
        + " 364=" + str(len(s364))
        + " 361=" + str(len(s361))
    )
PY

%build
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
test -s %{pu_xml}

mkdir -p pu420/classes
find src/main/java -name '*.java' > pu420/sources.list
test -s pu420/sources.list
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp %{pu_xml} \
	-d pu420/classes @pu420/sources.list
/bin/cp -a src/main/resources/. pu420/classes/
"$JAVA_HOME/bin/javac" --release 9 -encoding UTF-8 -Xlint:-options \
	-cp pu420/classes \
	-d pu420/classes/META-INF/versions/9 \
	src/main/java9/org/codehaus/plexus/util/BaseIOUtil.java
"$JAVA_HOME/bin/javac" --release 10 -encoding UTF-8 -Xlint:-options \
	-cp pu420/classes \
	-d pu420/classes/META-INF/versions/10 \
	src/main/java10/org/codehaus/plexus/util/BaseIOUtil.java
"$JAVA_HOME/bin/javac" --release 11 -encoding UTF-8 -Xlint:-options \
	-cp pu420/classes \
	-d pu420/classes/META-INF/versions/11 \
	src/main/java11/org/codehaus/plexus/util/BaseFileUtils.java
printf '%s\n' 'Manifest-Version: 1.0' 'Multi-Release: true' > pu420/manifest.mf
"$JAVA_HOME/bin/jar" cfm pu420/plexus-utils.jar pu420/manifest.mf -C pu420/classes .

for ver in 3.6.4 3.6.1; do
	top="plexus-utils-plexus-utils-${ver}"
	out="pu${ver}"
	mkdir -p "${out}/classes"
	find "${top}/src/main/java" -name '*.java' ! -name 'module-info.java' > "${out}/sources.list"
	test -s "${out}/sources.list"
	"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
		-d "${out}/classes" @"${out}/sources.list"
	/bin/cp -a "${top}/src/main/resources/." "${out}/classes/"
	"$JAVA_HOME/bin/jar" cf "${out}/plexus-utils.jar" -C "${out}/classes" .
done

python - << 'PY'
import zipfile
from pathlib import Path

def pom(version, optional_xml):
    deps = ""
    if optional_xml:
        deps = """  <dependencies>
    <dependency>
      <groupId>org.codehaus.plexus</groupId>
      <artifactId>plexus-xml</artifactId>
      <version>4.0.0</version>
      <optional>true</optional>
    </dependency>
  </dependencies>
"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.codehaus.plexus</groupId>
  <artifactId>plexus-utils</artifactId>
  <version>""" + version + """</version>
  <name>Plexus Common Utilities</name>
  <description>Utility classes shared by Plexus components.</description>
  <url>https://codehaus-plexus.github.io/plexus-utils/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
""" + deps + "</project>\n"

def major(z, name):
    data = z.read(name)
    return int.from_bytes(data[6:8], "big")

Path("pu420/plexus-utils.pom").write_text(pom("%{version}", True), encoding="utf-8")
Path("pu3.6.4/plexus-utils.pom").write_text(pom("3.6.4", False), encoding="utf-8")
Path("pu3.6.1/plexus-utils.pom").write_text(pom("3.6.1", False), encoding="utf-8")
z = zipfile.ZipFile("pu420/plexus-utils.jar")
names = z.namelist()
if any("Xpp3" in name for name in names):
    raise SystemExit("Xpp3 leaked into 4.2.0")
checks = {
    "org/codehaus/plexus/util/StringUtils.class": 52,
    "META-INF/versions/9/org/codehaus/plexus/util/BaseIOUtil.class": 53,
    "META-INF/versions/10/org/codehaus/plexus/util/BaseIOUtil.class": 54,
    "META-INF/versions/11/org/codehaus/plexus/util/BaseFileUtils.class": 55,
}
for name, want in checks.items():
    got = major(z, name)
    if got != want:
        raise SystemExit(name + " major " + str(got))
for ver in ("3.6.4", "3.6.1"):
    side = zipfile.ZipFile("pu" + ver + "/plexus-utils.jar")
    if "org/codehaus/plexus/util/xml/Xpp3Dom.class" not in side.namelist():
        raise SystemExit("Xpp3Dom missing from " + ver)
PY

%install
export JAVA_HOME=%{_jvmdir}/java-openjdk
pin_side() {
	ver="$1"
	sysjar install --buildroot %{buildroot} \
		--artifact "pu${ver}/plexus-utils.pom:pu${ver}/plexus-utils.jar" \
		--file-name "plexus-utils-${ver}" \
		--filelist ".mfiles${ver}"
	/bin/mv %{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils.sysjar \
		%{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils-${ver}.sysjar
	sed -i "s|/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils\\.sysjar|/usr/share/sysjar/index/org.codehaus.plexus/plexus-utils-${ver}.sysjar|" ".mfiles${ver}"
}
pin_side 3.6.1
pin_side 3.6.4
sysjar install --buildroot %{buildroot} \
	--artifact pu420/plexus-utils.pom:pu420/plexus-utils.jar \
	--file-name plexus-utils \
	--filelist .mfiles
for extra in .mfiles3.6.1 .mfiles3.6.4; do
	while IFS= read -r line; do
		grep -qxF -- "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
	done < "$extra"
done

%check
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
cat > PuSmoke.java << 'EOF'
import java.io.ByteArrayInputStream;
import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;
import org.codehaus.plexus.util.ReaderFactory;
import org.codehaus.plexus.util.StringUtils;
public class PuSmoke {
	public static void main(String[] args) throws Exception {
		String out = StringUtils.join(new String[] {"a", "b"}, ",");
		if (!"a,b".equals(out)) {
			throw new AssertionError(out);
		}
		byte[] xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><a/>".getBytes("UTF-8");
		String enc = ReaderFactory.newXmlReader(new ByteArrayInputStream(xml)).getEncoding();
		if (enc == null || enc.isEmpty()) {
			throw new AssertionError("no encoding");
		}
		File jar = new File(args[1]);
		URL[] urls = new URL[] { jar.toURI().toURL() };
		URLClassLoader loader = new URLClassLoader(urls, null);
		boolean hasXpp;
		try {
			Class.forName("org.codehaus.plexus.util.xml.Xpp3Dom", false, loader);
			hasXpp = true;
		} catch (ClassNotFoundException ex) {
			hasXpp = false;
		} finally {
			loader.close();
		}
		System.out.println(args[0] + " " + out + " xpp=" + hasXpp + " enc=" + enc);
	}
}
EOF
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -Xlint:-options \
	-cp "%{buildroot}%{_javadir}/plexus-utils.jar:%{pu_xml}" PuSmoke.java
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/plexus-utils.jar:%{pu_xml}:." PuSmoke pu420_ok %{buildroot}%{_javadir}/plexus-utils.jar > check420.log
cat check420.log
grep -F -qx 'pu420_ok a,b xpp=false enc=UTF-8' check420.log
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/plexus-utils-3.6.4.jar:." PuSmoke pu364_ok %{buildroot}%{_javadir}/plexus-utils-3.6.4.jar > check364.log
cat check364.log
grep -F -qx 'pu364_ok a,b xpp=true enc=UTF-8' check364.log
"$JAVA_HOME/bin/java" -cp "%{buildroot}%{_javadir}/plexus-utils-3.6.1.jar:." PuSmoke pu361_ok %{buildroot}%{_javadir}/plexus-utils-3.6.1.jar > check361.log
cat check361.log
grep -F -qx 'pu361_ok a,b xpp=true enc=UTF-8' check361.log

%files -f .mfiles
%license LICENSE.txt
%doc NOTICE.txt README.md
