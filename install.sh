#/bin/bash

cp ./grub2-select.py /usr/sbin/grub2-select

# hook it to the reboot utility
mv /usr/sbin/reboot /usr/sbin/do_reboot
touch /usr/sbin/reboot
chmod a+x /usr/sbin/reboot
echo "grub2-select && do_reboot" > /usr/sbin/reboot
