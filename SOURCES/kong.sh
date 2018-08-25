#!/bin/bash
eval $(/usr/local/openresty/luajit/bin/luajit /usr/local/bin/luarocks path --tree /usr/local/kong/)
/usr/local/openresty/bin/resty /usr/local/kong/kong.lua $@
