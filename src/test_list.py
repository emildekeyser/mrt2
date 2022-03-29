#!/usr/bin/python

#   |directory   |script name               |enquable?|displayname
checks = [
    ['ping',     'check_ping.sh',           True],
    ['git',      'check_git.sh',            False],
    ['ssh',      'check_ssh.sh',            True],
    ['locale',   'check_locale.sh',         True],
    ['backup',   'check_backup.sh',         True],
    ['sudo',     'check_sudo.sh',           True],
    ['upgrade',  'check_debian_version.sh', True],
    ['apt',      'check_apt.sh',            True],
    ['arp',      'check_static_arp.sh',     False],
    ['ntp',      'check_ntp.sh',            True],
    ['dns',      'check_dns.sh',            True],
    ['http',     'check_http.sh',           True],
    ['https',    'check_https.sh',          True],
    ['mysql',    'check_mysql.sh',          True],
    ['smtp',     'check_smtp.sh',           True,   'smtp'],
    ['smtp',     'check_imap.sh',           True,   'imap'],
    ['ipv6',     'check_ipv6.sh',           True],
    ['ipv6_2',   'check_ipv6_2.sh',         True,   'ipv6 cert'],
    ['mystery1', 'check_myst1.sh',          True],
    ['firewall', 'check_firewall.sh',       False],
    ['ansible',  'check_ansible.sh',        False],
    ['dnssec',   'check_dnssec.sh',         False],
    ['radius',   'check_radius_1.sh',       False],
    ['netflow',  'check_netflow.sh',        False],
]
