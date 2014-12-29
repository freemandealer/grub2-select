#! /usr/bin/env python

import os
import sys
import StringIO

class grub2select():
    menuCount = 1
    menuData = {}
    grub2cfgData = StringIO.StringIO()
    grubEnvData = StringIO.StringIO()
    grub2cfg = "/boot/grub2/grub.cfg"
    grubDefault = str(None)
    grubDefaultMatch = None
    

    def parseGrubCfg(self):
        """read in 'grub.cfg' and 'grub2-editenv list' and parse data"""
        if not os.path.exists(self.grub2cfg):
            print("unable to locate %s, is grub2 installed?" % self.grub2cfg)
            sys.exit(0)


        # load grub.cfg menu data
        self.grub2cfgData = StringIO.StringIO()
        f = open("/boot/grub2/grub.cfg", "r")
        self.grub2cfgData.write(f.read())
        f.close()
        del(f)
        self.grub2cfgData.seek(0)

        # load grub2 env data
        self.grubEnvData = StringIO.StringIO()
        os.system("grub2-editenv list > /tmp/grub2-env.lst")
        f = open("/tmp/grub2-env.lst", "r")
        self.grubEnvData.write(f.read())
        f.close()
        del(f)
        self.grubEnvData.seek(0)

        # parse grub.cfg data
        self.menuData = {}
        self.menuCount = 1
        self.grub2cfgData.seek(0)
        for line in self.grub2cfgData:
            if line.strip().lower().startswith("menuentry "):
                menu = {"name": None, "id": None}
                menu["name"] = line.split("'")[1]
                menu["id"] = line.split("'")[3]
                self.menuData[self.menuCount] = menu
                self.menuCount +=1
                
        # parse grubEnv for default
        self.grubDefault = str(None)
        self.grubDefaultMatch = None
        for line in self.grubEnvData:
            if line.lower().startswith("saved_entry="):
                self.grubDefault = line.replace("saved_entry=", "").strip()

        # try to match default => menu["id"]
        for item in sorted(self.menuData):
            if str(self.menuData[item]["id"]).count(self.grubDefault):
                self.grubDefaultMatch = item
        # try to match default => menu["name"]
        for item in sorted(self.menuData):
            try:
                matchData = self.grubDefault.split(">")[1]
            except:
                matchData = self.grubDefault
            if self.menuData[item]["name"].count(matchData):
                self.grubDefaultMatch = item

    def selectKernel(self):
        for item in sorted(self.menuData):
            if item is self.grubDefaultMatch:
                grubMatch = "*"
            else:
                grubMatch = " "
            print("{0}:{2}:{1}".format(item, self.menuData[item]["name"], grubMatch))
        print("")
        self.showGrubDefault()
        selection = raw_input("select number: ")
        if not selection.isdigit():
            print("Invalid selection")
            sys.exit(0)

        try:
            selection = int(selection)
        except:
            print("Invalid selection")
            sys.exit(0)
        if (selection < 1) or (selection >= self.menuCount):
            print("Invalid selection")
            sys.exit(0)
        print("valid selection!\n")

        os.system('grub2-set-default "{0}"'.format(self.menuData[selection]["id"]))
        os.system('grub2-mkconfig -o /boot/grub2/grub.cfg')

    def showGrubDefault(self):
        if self.grubDefaultMatch is not None:
            print("Current Default: {0}".format(self.menuData[self.grubDefaultMatch]["name"]))
        else:
            print("Current Default: UNKNOWN")
    
    def main(self):
        self.parseGrubCfg()
        self.selectKernel()
        self.parseGrubCfg()
        self.showGrubDefault()

if __name__ == "__main__":
    try:
        program = grub2select()
        program.main()
    except KeyboardInterrupt:
        print("Bye!")
        sys.exit(0)
