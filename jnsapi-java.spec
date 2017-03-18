%{?_javapackages_macros:%_javapackages_macros}

%define commit eb9f88c68ee6e1c9f9de533ac6c46f5fea458ad8
%define shortcommit %(c=%{commit}; echo ${c:0:7})

%define oname jnsapi

Summary:	An Open Source Java base library for XMPP
Name:		%{oname}-java
Version:	0.4.1
Release:	0
License:	ASL 2.0
Group:		Development/Java
URL:		https://github.com/archling/jinglenodes/
# git clone https://github.com/archling/jinglenodes.git jinglenodes-code
# cp -a jinglenodes-code/jnsapi_java jnsapi-java-0.4.1
# tar --exclude .git -cvJf jnsapi-java-0.4.1.tar.xz jnsapi-java-0.4.1
Source0:	%{name}-%{version}.tar.xz
Patch0:		 %{name}-0.4.1-pom_xml.patch
# Jitsi calls deepSearch method directly!
Patch1:		 %{name}-0.4.1-deepSearch.patch
BuildArch:	noarch

BuildRequires:	maven-local
BuildRequires:	mvn(commons-lang:commons-lang)
BuildRequires:	mvn(dom4j:dom4j)
BuildRequires:	mvn(log4j:log4j)
BuildRequires:	mvn(junit:junit)
BuildRequires:	mvn(org.jitsi:smack)
BuildRequires:	mvn(org.jitsi:smackx)

%description
JXMPP is an Open Source Java base library for XMPP. It provides often
used functionality needed to build a XMPP stack.

%files -f .mfiles

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc

#----------------------------------------------------------------------------

%prep
%setup -q
# Delete prebuild JARs and docs
find . -type f -name "*.jar" -delete
find . -type f -name "*.class" -delete

# Apply all aptches
%patch0 -p1 -b .orig
%patch1 -p1 -b .orig

# Fix missing version warnings
%pom_xpath_inject "pom:plugin[pom:artifactId[./text()='maven-compiler-plugin']]" "
	<version>any</version>"

# Fix groupId for Jitsi smack fork according to jitsi-smack package
%pom_xpath_replace "pom:dependency[pom:artifactId[./text()='smack']]/pom:groupId" "
	<groupId>org.jitsi</groupId>" .
%pom_xpath_replace "pom:dependency[pom:artifactId[./text()='smackx']]/pom:groupId" "
	<groupId>org.jitsi</groupId>"

# Add an OSGi compilant MANIFEST.MF
%pom_add_plugin org.apache.felix:maven-bundle-plugin . "
<extensions>true</extensions>
<configuration>
	<supportedProjectTypes>
		<supportedProjectType>bundle</supportedProjectType>
		<supportedProjectType>jar</supportedProjectType>
	</supportedProjectTypes>
	<instructions>
		<Bundle-Name>\${project.artifactId}</Bundle-Name>
		<Bundle-Version>\${project.version}</Bundle-Version>
	</instructions>
</configuration>
<executions>
	<execution>
		<id>bundle-manifest</id>
		<phase>process-classes</phase>
		<goals>
			<goal>manifest</goal>
		</goals>
	</execution>
</executions>"

# Add the META-INF/INDEX.LIST (fix jar-not-indexed warning) and
# the META-INF/MANIFEST.MF to the jar archive
%pom_add_plugin :maven-jar-plugin . "
<executions>
	<execution>
		<phase>package</phase>
		<configuration>
			<archive>
				<manifestFile>\${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
				<manifest>
					<addDefaultImplementationEntries>true</addDefaultImplementationEntries>
					<addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
				</manifest>
				<index>true</index>
			</archive>
		</configuration>
		<goals>
			<goal>jar</goal>
		</goals>
	</execution>
</executions>"

# Fix JAR name
%mvn_file :%{name} %{name}-%{version} %{name}

%build
# Lots of tests fail
%mvn_build -f -- -Dproject.build.sourceEncoding=UTF-8 -Dmaven.compiler.source=1.7 -Dmaven.compiler.target=1.7

%install
%mvn_install

