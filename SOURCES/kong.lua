#!/usr/local/openresty/bin/resty

local version = _VERSION:match("%d+%.%d+")
package.path = '/usr/local/kong/share/lua/' .. version .. '/?.lua;/usr/local/kong/share/lua/' .. version .. '/?/init.lua' .. package.path
package.cpath = '/usr/local/kong/lib/lua/' .. version .. '/?.so' .. package.cpath

require("kong.cmd.init")(arg)
