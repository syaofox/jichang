#!/bin/sh
exec >/tmp/setup.log 2>&1

root_password="0928"
lan_ip_address="10.10.10.20/24"

# --- 1. 设置密码 ---
if [ -n "$root_password" ]; then
  printf "%s\n%s\n" "$root_password" "$root_password" | passwd root
fi

# --- 2. 配置旁路由网络 (LAN) ---
if [ -n "$lan_ip_address" ]; then
  uci set network.lan.proto='static'
  uci set network.lan.ipaddr="$lan_ip_address"
  uci set network.lan.gateway='10.10.10.1'
  uci del network.lan.dns
  uci add_list network.lan.dns='10.10.10.1'
  uci add_list network.lan.dns='223.5.5.5'
  
  # 禁用 DHCP 服务，防止冲突
  uci set dhcp.lan.ignore='1'
  uci set dhcp.lan.ra='disabled'
  uci set dhcp.lan.dhcpv6='disabled'
  
  uci commit network
  uci commit dhcp
fi

# 旁路由防火墙优化 ---
uci set firewall.@zone[0].masq='1'
uci set firewall.@zone[0].mtu_fix='1'
uci commit firewall

echo "Setup Complete!"