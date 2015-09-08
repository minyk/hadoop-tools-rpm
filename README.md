Hadoop Tools RPM
=================

# Build

```
$ ./hadoop-tools-rpm.sh
```

# Output

RPM package should be placed in the `RPMS/x86_64` directory like this:

`RPMS/x86_64/hadoop-tools-X.X.X-X.x86_64.rpm`

# Change Version

Edit the following line in the `hadoop-tools-rpm.sh`:

```
HADOOP_VERSION="2.6.0"
```