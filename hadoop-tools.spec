# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Hadoop RPM spec file
#

# FIXME: we need to disable a more strict checks on native files for now,
# since Hadoop build system makes it difficult to pass the kind of flags
# that would make newer RPM debuginfo generation scripts happy.
%undefine _missing_build_ids_terminate_build

%define name hadoop-tools
%define hadoop_name hadoop
%define lib_hadoop_dirname /usr/lib
%define lib_hadoop_tools %{lib_hadoop_dirname}/%{name}
%define hadoop_build_path build
%define libexecdir /usr/lib

%ifarch i386
%global hadoop_arch Linux-i386-32
%endif
%ifarch amd64 x86_64
%global hadoop_arch Linux-amd64-64
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0

# FIXME: brp-repack-jars uses unzip to expand jar files
# Unfortunately aspectjtools-1.6.5.jar pulled by ivy contains some files and directories without any read permission
# and make whole process to fail.
# So for now brp-repack-jars is being deactivated until this is fixed.
# See BIGTOP-294
%define __os_install_post \
    /usr/lib/rpm/redhat/brp-compress ; \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} ; \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} ; \
    /usr/lib/rpm/brp-python-bytecompile ; \
    %{nil}

%define netcat_package nc
%define doc_hadoop %{_docdir}/%{name}-%{hadoop_version}
%define alternatives_cmd alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d
%endif


%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# Deactivating symlinks checks
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

%define netcat_package netcat-openbsd
%define doc_hadoop %{_docdir}/%{name}
%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d
%endif

%if  0%{?mgaversion}
%define netcat_package netcat-openbsd
%define doc_hadoop %{_docdir}/%{name}-%{hadoop_version}
%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d
%endif


# Even though we split the RPM into arch and noarch, it still will build and install
# the entirety of hadoop. Defining this tells RPM not to fail the build
# when it notices that we didn't package most of the installed files.
%define _unpackaged_files_terminate_build 0

# RPM searches perl files for dependancies and this breaks for non packaged perl lib
# like thrift so disable this
%define _use_internal_dependency_generator 0

Name: %{name}
Version: %{hadoop_version}
Release: %{hadoop_release}
Summary: Hadoop Tools JARS
License: ASL 2.0
URL: http://hadoop.apache.org/core/
Group: Development/Libraries
Source0: %{hadoop_name}-%{hadoop_base_version}.tar.gz
Source1: do-component-build
Source2: install_%{name}.sh
#BIGTOP_PATCH_FILES
Buildroot: %{_tmppath}/%{hadoop_name}-%{version}-%{release}-root-%(%{__id} -u -n)
BuildRequires: fuse-devel, fuse, cmake
Requires: coreutils, /usr/sbin/useradd, /usr/sbin/usermod, /sbin/chkconfig, /sbin/service, bigtop-utils >= 0.7, zookeeper >= 3.4.0
Requires: psmisc, %{netcat_package}, hadoop >= %{version}
# Sadly, Sun/Oracle JDK in RPM form doesn't provide libjvm.so, which means we have
# to set AutoReq to no in order to minimize confusion. Not ideal, but seems to work.
# I wish there was a way to disable just one auto dependency (libjvm.so)
AutoReq: no

%if  %{?suse_version:1}0
BuildRequires: pkg-config, libfuse2, libopenssl-devel, gcc-c++
%endif

%description
Hadoop Tools Packages.

%prep
%setup -n %{hadoop_name}-release-%{hadoop_base_version}

#BIGTOP_PATCH_COMMANDS
%build
# This assumes that you installed Java JDK 6 and set JAVA_HOME
# This assumes that you installed Forrest and set FORREST_HOME

env HADOOP_VERSION=%{hadoop_base_version} HADOOP_ARCH=%{hadoop_arch} bash %{SOURCE1}

%clean
%__rm -rf $RPM_BUILD_ROOT

#########################
#### INSTALL SECTION ####
#########################
%install
%__rm -rf $RPM_BUILD_ROOT

%__install -d -m 0755 $RPM_BUILD_ROOT/%{lib_hadoop}

env HADOOP_VERSION=%{hadoop_base_version} bash %{SOURCE2} \
  --distro-dir=$RPM_SOURCE_DIR \
  --build-dir=$PWD/build \
  --system-include-dir=$RPM_BUILD_ROOT%{_includedir} \
  --system-lib-dir=$RPM_BUILD_ROOT%{_libdir} \
  --system-libexec-dir=$RPM_BUILD_ROOT/%{lib_hadoop}/libexec \
  --prefix=$RPM_BUILD_ROOT \
  --native-build-string=%{hadoop_arch} \
  --installed-lib-dir=%{lib_hadoop} \

%post
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-ant-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-ant.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-archives-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-archives.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-auth-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-auth.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-aws-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-aws.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-datajoin-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-datajoin.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-distcp-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-distcp.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-extras-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-extras.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-gridmix-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-gridmix.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-openstack-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-openstack.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-rumen-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-rumen.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-sls-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-sls.jar
%__ln_s /usr/lib/hadoop-tools/lib/hadoop-streaming-%{hadoop_base_version}.jar /usr/lib/hadoop-tools/hadoop-streaming.jar

%files
%defattr(-,root,root)
%{lib_hadoop_tools}/lib
