
all: package

package: package/zypp-plugin-spacewalk.tar.bz2

package/zypp-plugin-spacewalk.tar.bz2:
	git archive --format=tar --prefix=zypp-plugin-spacewalk/ HEAD  | bzip2 -c > package/zypp-plugin-spacewalk.tar.bz2
clean:
	rm -rf package/zypp-plugin-spacewalk.tar.bz2
