# fgDeepConfCompare

Comparing fortigate configurations pre and post upgrade might be tricky as in some cases configuration sections are just changed in position, this can also happen in ha cluster with an high number of vdoms the difference is in the position of the vdom, so there is no real difference in the configuration itself. The standard file compare tools like vimdiff, notepad++, ecc. can't spot this as they are general purpose compare tools which are comparing files based of buffers of lines.<br>

This tool is extracting each vdom and each configuration section by context and compare between the two configuration regardless the position in the configuration file. <br>
This is done with good performances, I was able to compare two configurations with 1.1M lines in 25 seconds (with 8 concurrent threads)<br>


USAGE<br>

./fgDeepConfCompare.py <conf1 name> <conf2 name><br>

The script will automatically detect vdoms if present and compare them one by one. The output is logged on the cli and to the file "confcompare_output.log" on the script location.<br>

OUTPUT<br>

./fgDeepConfCompare.py  fgt1.conf fgt2.conf<br>
[+] Processing vdom: root<br>
[+] Processing vdom: VD1<br>
[+] Processing vdom: VD2<br>
+---------------------------------------------------------------------------------------+<br>
[*] Checking vdom: global<br>
vdom len in conf 1: 11698<br>
vdom len in conf 2: 10214<br>
[!] differences in: config system global<br>
First Conf:<br>
config system global<br>
    set admin-scp enable<br>
    set admintimeout 10<br>
    set gui-ipv6 enable<br>
    set gui-theme mariner<br>
    set hostname "FGT-1"<br>
    set switch-controller enable<br>
    set timezone 31<br>
    set vdom-mode multi-vdom<br>
    set edit-vdom-prompt enable<br>
end<br>
Second Conf:<br>
config system global<br>
    set admin-scp enable<br>
    set admintimeout 30<br>
    set gui-ipv6 enable<br>
    set gui-theme mariner<br>
    set hostname "FGT-2"<br>
    set switch-controller enable<br>
    set timezone 31<br>
    set vdom-mode multi-vdom<br>
    set edit-vdom-prompt enable<br>
end<br>
[!] differences in: config system interface    <<< all the configuration section longer than 20 lines are only logged to file<br>
[!] differences in: config system admin<br>
[!] differences in: config system ha<br>
[!] differences in: config firewall internet-service-name<br>
[!] differences in: config certificate local<br>
[!] differences in: config system vdom-property<br>
[!] differences in: config firewall ssh local-key<br>
[!] differences in: config firewall ssh local-ca<br>
**[!] Diff spotted on conf1 > conf2 check for vdom: global**  <<< by default the configuration is checked from conf1 to conf2, if no differences are spotted then the check is also done in the reverse way<br>
+---------------------------------------------------------------------------------------+<br>
[*] Checking vdom: root<br>
**vdom len in conf 1: 1612**<br>
**vdom len in conf 2: 1809**<br>
[!] differences in: config firewall ssh local-key<br>
conf section not existing in Second config<br>
[!] differences in: config firewall ssh local-ca<br>
conf section not existing in Second config<br>
**[!] Diff spotted on conf2 > conf1 check for vdom: root**   <<< the initial conf1 checked against conf2 didn't find differences, the reverse check highlighted that there are part of the configuration that are not present in conf1 <br>
+---------------------------------------------------------------------------------------+<br>
[*] Checking vdom: VD1<br>
vdom len in conf 1: 18890<br>
vdom len in conf 2: 18890<br>
[+] No differences spotted in both ways checks for vdom: VD1  <<< the hash of saved passwords is triggering the deeper check configuration section by configuration section, but then this check shows that there are no real differences as I'm excluding every lines with the fortigate hashes in line. Script line 153<br>

				if re.search("\w+ ENC .{15,}", line):
					pass
     
+---------------------------------------------------------------------------------------+<br>
[+] vdom: VD2 are the same<br>
+---------------------------------------------------------------------------------------+<br>
