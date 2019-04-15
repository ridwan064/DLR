

data="$(pdsh -w cosbench 'sh cos/cli.sh info')"
echo "${data[1]}"



