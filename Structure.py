#!/usr/bin/env python
# -*- coding: utf-8  -*-

# ****************************************************************************
#  This program is free software; you can redistribute it and/or modify 
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# 
# ****************************************************************************


"""

(C) 2020 by Peter Hanzel, <hanzelpeter@gmail.com>, https://www.hanzelpeter.com
USAGE

Select a textframe

"""

try:
    import scribus
    import json
except ImportError:
    print ("Unable to import the 'scribus' module. This script will only run within")
    print ("the Python interpreter embedded in Scribus. Try Script->Execute Script.")
    sys.exit(1)

def findElemById(elemId):
    
    pageitems = scribus.getPageItems()
    for item in pageitems:

        felemId = 0;

        if (len(item)>1 and item[1] == 4):
            #scribus.messageBox('dde', str(item[0]), scribus.ICON_WARNING, scribus.BUTTON_OK)

            attrs = scribus.getObjectAttributes(item[0]);
            if (len(attrs)>1):
                #scribus.messageBox('dde', str(attrs[1]), scribus.ICON_WARNING, scribus.BUTTON_OK)
                felemId = int(attrs[1]['Value']);
                #scribus.messageBox('ddx', str(type(felemId)))

        if (felemId == elemId):
            return item[0];
    return None; 

def dumpElem(elem):
    attrs = scribus.getObjectAttributes(elem);
    
    if (len(attrs)<2):
        return "<INVALID>";

    elemName = attrs[0]['Value'];
    parent = attrs[0]['RelationshipTo'];
    text = scribus.getText(elem);

    elemId = attrs[1]['Value'];

    allNames = '' #json.dumps(attrs);
    allNames = '' #str(attrs);

    return elemName + '[@id=' + elemId + '] parent:(' + parent + ') text:' + text;

def getParentElemId(elem):
    attrs = scribus.getObjectAttributes(elem);
    if (len(attrs)<1):
        return -1;

    parent = attrs[0]['RelationshipTo'];

    if (parent == 'root'):
          return -1;

    index = parent.find(']');
    return int(parent[1:index]);

def getElemId(elem):
    attrs = scribus.getObjectAttributes(elem);
    if (len(attrs)<2):
        return -1;

    elemId = int(attrs[1]['Value']);
    return elemId;

def main(argv):

    unit = scribus.getUnit()
    units = [' pts','mm',' inches',' picas','cm',' ciceros']
    unitlabel = units[unit]
    if scribus.selectionCount() == 0:
        scribus.messageBox('Scribus - Script Error',
            "There is no object selected.\nPlease select a text frame and try again.",
            scribus.ICON_WARNING, scribus.BUTTON_OK)
        sys.exit(2)
    if scribus.selectionCount() > 1:
        scribus.messageBox('Scribus - Script Error',
            "You have more than one object selected.\nPlease select one text frame and try again.",
            scribus.ICON_WARNING, scribus.BUTTON_OK)
        sys.exit(2)

    textbox = scribus.getSelectedObject()
    pageitems = scribus.getPageItems()
    boxcount = 1
    for item in pageitems:
        if (item[0] == textbox):
            if (item[1] != 4):
                scribus.messageBox('Scribus - Script Error', 
                          "This is not a textframe. Try again.", scribus.ICON_WARNING, scribus.BUTTON_OK)
                sys.exit(2)

# While we're finding out what kind of frame is selected, we'll also make sure we
# will come up with a unique name for our infobox frame - it's possible we may want
# more than one for a multicolumn frame.
        if (item[0] == ("infobox" + str(boxcount) + textbox)):
                boxcount += 1

    elem = textbox;
    pathUp = '';

    while elem != None:
        elemId = getElemId(elem);
        pElemId = getParentElemId(elem);
        pathUp = dumpElem(elem) + " // " +  pathUp;
        elem = findElemById(pElemId);

    if (pathUp != ''):
        pathUp = pathUp[0:len(pathUp)-4];

    #framename = scribus.valueDialog('XML Tree','XML Tree', elemName + '[@id=' + elemId + '] parent: ' + parent + ' text:' + text + "," + parent)
    framename = scribus.valueDialog('XML Tree','XML Tree (Path UP)', pathUp);

    if (not framename) :
        sys.exit(0)

if __name__ == '__main__':
    # This script makes no sense without a document open
    if not scribus.haveDoc():
        scribus.messageBox('Scribus - Script Error', "No document open", scribus.ICON_WARNING, scribus.BUTTON_OK)
        sys.exit(1)
    # Disable redraws
    scribus.setRedraw(False)
    # Run the main script, ensuring redraws are re-enabled even if the
    # script aborts with an exception, and don't fail with an exception
    # even if the document is closed while the script runs.
    try:
        main(sys.argv)
    finally:
        try:
            scribus.setRedraw(True)
        except:
            pass