# fgDeepConfCompare

Comparing fortigate configurations pre and post upgrade might be tricky as in some cases configuration sections are just changed in position, this can also happen in ha cluster with an high number of vdoms the difference is in the position of the vdom, so there is no real difference in the configuration itself. The standard file compare tools like vimdiff, notepad++, ecc. can't spot this as they are general purpose compare tools which are comparing files based of buffers of lines.

This tool is extracting each vdom and each configuration section by context and compare between the two configuration regardless the position in the configuration file. 
This is done with good performances, I was able to compare two configurations with 1.1M lines in 25 seconds (with 8 concurrent threads)

USAGE

./fgDeepConfCompare.py <conf1 name> <conf2 name>

The script will automatically detect vdoms if present and compare them one by one. The output is logged on the cli and to the file "confcompare_output.log" on the script location.

OUTPUT

./fgDeepConfCompare.py  fgt1.conf fgt2.conf
[+] Processing vdom: root
[+] Processing vdom: VD1
[+] Processing vdom: VD2
+---------------------------------------------------------------------------------------+
[*] Checking vdom: global
vdom len in conf 1: 11698
vdom len in conf 2: 10214
[!] differences in: config system global
First Conf:
config system global
    set admin-scp enable
    set admintimeout 10
    set alias "FGT-1"
    set gui-ipv6 enable
    set gui-theme mariner
    set hostname "OreMSC1NFW01"
    set switch-controller enable
    set timezone 31
    set vdom-mode multi-vdom
    set edit-vdom-prompt enable
end
Second Conf:
config system global
    set admin-scp enable
    set admintimeout 30
    set gui-ipv6 enable
    set gui-theme mariner
    set hostname "FGT-2"
    set switch-controller enable
    set timezone 31
    set vdom-mode multi-vdom
    set edit-vdom-prompt enable
end
[!] differences in: config system interface    <<< all the configuration section longer than 20 lines are only logged to file
[!] differences in: config system admin
[!] differences in: config system ha
[!] differences in: config firewall internet-service-name
[!] differences in: config certificate local
[!] differences in: config system vdom-property
[!] differences in: config firewall ssh local-key
[!] differences in: config firewall ssh local-ca
**[!] Diff spotted on conf1 > conf2 check for vdom: global**  <<< by default the configuration is checked from conf1 to conf2, if no differences are spotted then the check is also done in the reverse way
+---------------------------------------------------------------------------------------+
[*] Checking vdom: root
**vdom len in conf 1: 1612
vdom len in conf 2: 1809**
[!] differences in: config firewall ssh local-key
conf section not existing in Second config
[!] differences in: config firewall ssh local-ca
conf section not existing in Second config
**[!] Diff spotted on conf2 > conf1 check for vdom: root**   <<< the initial conf1 checked against conf2 didn't find differences, the reverse check highlighted that there are part of the configuration that are not present in conf1 
+---------------------------------------------------------------------------------------+
[*] Checking vdom: VD1
vdom len in conf 1: 18890
vdom len in conf 2: 18890
[+] No differences spotted in both ways checks for vdom: VD1  <<< the hash of saved passwords is triggering the deeper check configuration section by configuration section, but then this check shows that there are no real differences as I'm excluding every lines with the fortigate hashes in line. Script line 153

				if re.search("\w+ ENC .{15,}", line):
					pass
     
+---------------------------------------------------------------------------------------+
[+] vdom: VD2 are the same
+---------------------------------------------------------------------------------------+
