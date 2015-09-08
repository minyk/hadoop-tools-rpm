#!/bin/sh
NAME="HADOOP-TOOLS"
PKGNAME="hadoop-tools"
HADOOP_PKGNAME="hadoop"
HADOOP_VERSION="2.6.0"
GITHUB_RELEASE="release-${HADOOP_VERSION}"
GITHUB_URL="https://github.com/apache/hadoop/archive"
BASE_VERSION=${HADOOP_VERSION}
RELEASE="0"

set -ex

rm -rf BUILD BUILDROOT SOURCES RPMS SRPMS tmp || true
mkdir -p BUILD RPMS SRPMS SOURCES

if [ ! -f SOURCES/${HADOOP_PKGNAME}-${HADOOP_VERSION}.tar.gz ];
then
    curl --retry 5 -# -L -k -o SOURCES/${HADOOP_PKGNAME}-${HADOOP_VERSION}.tar.gz ${GITHUB_URL}/${GITHUB_RELEASE}.tar.gz
fi

cp bigtop.bom SOURCES/bigtop.bom
cp ${PKGNAME}/* SOURCES/

rpmbuild -ba --define="_topdir $PWD" --define="_tmppath $PWD/tmp" \
 --define="hadoop_version ${HADOOP_VERSION}" \
 --define="hadoop_base_version ${BASE_VERSION}" \
 --define="hadoop_release ${RELEASE}" \
 ${PKGNAME}.spec
