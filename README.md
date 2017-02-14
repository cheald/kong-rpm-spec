## Kong RPM Build Specs

These are RPM build specs for [Kong](https://getkong.org), which will build and package:

* OpenResty (1.11.2.2)
* Luarocks (2.4.2)
* Serf (0.8.0)
* Kong (0.10.0/HEAD prerelease) 

Additionally, the RPM includes an init.d file providing service control for kong.

## Selecting Build Target

* Edit SOURCES/kong-patch-spec.patch
	* Replace `version` with the release or refspec of the rockspec to build
	* Replace `branch` with the desired build target - luarocks will clone this target for installation
	* If not building `kong-0.10.0rc3-0.rockspec`, replace `rockfile` in `SPECS/kong.lua` with the proper rockspec

## Building

    cd SPECS
    spectool -g -R kong.spec
    rpmbuild -ba kong.spec
