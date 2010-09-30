
all: package

package: package/zypp-plugin-spacewalk.tar.bz2

package/zypp-plugin-spacewalk.tar.bz2:
	tar --transform 's,^,zypp-plugin-spacewalk/,' -jcf package/zypp-plugin-spacewalk.tar.bz2 bin/ python/

clean:
	rm -rf package/zypp-plugin-spacewalk.tar.bz2
