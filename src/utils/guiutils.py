# def guisave(self, settings):
#     # Save geometry
#     settings.setValue('size', self.size())
#     settings.setValue('pos', self.pos())

#     for name, obj in inspect.getmembers(ui):
#         # if type(obj) is QComboBox:  # this works similar to isinstance, but missed some field... not sure why?
#         if isinstance(obj, QComboBox):
#             name = obj.objectName()  # get combobox name
#             index = obj.currentIndex()  # get current index from combobox
#             text = obj.itemText(index)  # get the text for current index
#             # save combobox selection to registry
#             settings.setValue(name, text)

#         if isinstance(obj, QLineEdit):
#             name = obj.objectName()
#             value = obj.text()
#             # save ui values, so they can be restored next time
#             settings.setValue(name, value)

#         if isinstance(obj, QCheckBox):
#             name = obj.objectName()
#             state = obj.isChecked()
#             settings.setValue(name, state)

#         if isinstance(obj, QRadioButton):
#             name = obj.objectName()
#             value = obj.isChecked()  # get stored value from registry
#             settings.setValue(name, value)

# def guirestore(self, settings):
#     # Restore geometry
#     self.resize(settings.value('size', QtCore.QSize(500, 500)))
#     self.move(settings.value('pos', QtCore.QPoint(60, 60)))

#     for name, obj in inspect.getmembers(ui):
#         if isinstance(obj, QComboBox):
#             index = obj.currentIndex()  # get current region from combobox
#             # text   = obj.itemText(index)   # get the text for new selected index
#             name = obj.objectName()

#             value = (settings.value(name))

#             if value == "":
#                 continue

#             # get the corresponding index for specified string in combobox
#             index = obj.findText(value)

#             if index == -1:  # add to list if not found
#                     obj.insertItems(0, [value])
#                     index = obj.findText(value)
#                     obj.setCurrentIndex(index)
#             else:
#                 # preselect a combobox value by index
#                 obj.setCurrentIndex(index)

#         if isinstance(obj, QLineEdit):
#             name = obj.objectName()
#             # get stored value from registry
#             value = (settings.value(name).decode('utf-8'))
#             obj.setText(value)  # restore lineEditFile

#         if isinstance(obj, QCheckBox):
#             name = obj.objectName()
#             value = settings.value(name)  # get stored value from registry
#             if value != None:
#                 obj.setChecked(strtobool(value))  # restore checkbox

#         if isinstance(obj, QRadioButton):
#             name = obj.objectName()
#             value = settings.value(name)  # get stored value from registry
#             if value != None:
#                 obj.setChecked(strtobool(value))
