# The example of a multi-select dialog in a Kodi addon created with PyXBMCt framework.
# You will need a checkmark image file.
import os
import xbmcgui
import xbmcaddon
import pyxbmct.addonwindow as pyxbmct

_addon = xbmcaddon.Addon()
_path = _addon.getAddonInfo("path")
_check_icon = os.path.join(_path, "resources","check.png") # Don't decode _path to utf-8!!!


class MultiChoiceDialog(pyxbmct.AddonDialogWindow):
    def __init__(self, title="", items=None):
        super(MultiChoiceDialog, self).__init__(title)
        self.setGeometry(450, 300, 4, 4)
        self.selected = []
        self.set_controls()
        self.connect_controls()
        self.listing.addItems(items or [])
        self.set_navigation()

    def set_controls(self):
        self.listing = pyxbmct.List(_imageWidth=15)
        self.placeControl(self.listing, 0, 0, rowspan=3, columnspan=4)
        self.ok_button = pyxbmct.Button("OK")
        self.placeControl(self.ok_button, 3, 1)
        self.cancel_button = pyxbmct.Button("Cancel")
        self.placeControl(self.cancel_button, 3, 2)

    def connect_controls(self):
        self.connect(self.listing, self.check_uncheck)
        self.connect(self.ok_button, self.ok)
        self.connect(self.cancel_button, self.close)

    def set_navigation(self):
        self.listing.controlUp(self.ok_button)
        self.listing.controlDown(self.ok_button)
        self.ok_button.setNavigation(self.listing, self.listing, self.cancel_button, self.cancel_button)
        self.cancel_button.setNavigation(self.listing, self.listing, self.ok_button, self.ok_button)
        if self.listing.size():
            self.setFocus(self.listing)
        else:
            self.setFocus(self.cancel_button)

    def check_uncheck(self):
        list_item = self.listing.getSelectedItem()
        if list_item.getLabel2() == "checked":
            list_item.setIconImage("")
            list_item.setLabel2("unchecked")
        else:
            list_item.setIconImage(_check_icon)
            list_item.setLabel2("checked")

    def ok(self):
        self.selected = [index for index in xrange(self.listing.size())
                                if self.listing.getListItem(index).getLabel2() == "checked"]
        super(MultiChoiceDialog, self).close()

    def close(self):
        self.selected = []
        super(MultiChoiceDialog, self).close()

if __name__ == "__main__":
    items = ["Item {0}".format(i) for i in xrange(1, 11)]
    dialog = MultiChoiceDialog("Select items", items)
    dialog.doModal()
    xbmcgui.Dialog().notification("Finished", "Selected: {0}".format(str(dialog.selected)))
    del dialog #You need to delete your instance when it is no longer needed
    #because underlying xbmcgui classes are not grabage-collected.