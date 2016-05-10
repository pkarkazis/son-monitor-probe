# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import ConfigParser

__author__="panos"
__date__ ="$Dec 21, 2015 5:32:34 PM$"

if __name__ == "__main__":
    print "Read Configuration"
    
    
class configuration(object):
    def __init__(self, file):
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(file)
        

    def ConfigSectionMap(self,section):
        mdict = {}
        options = self.Config.options(section)
        for option in options:
            try:
                mdict[option] = self.Config.get(section, option)
                if mdict[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
        return mdict