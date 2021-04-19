class commandModule:
    def __init__(self, pCommandNameList, pModule, pModuleName, pEnableTrustet, pAllowedRoles):
        self.commandNameList = pCommandNameList
        self.module = pModule
        self.moduleName = pModuleName
        self.enableTrustet = pEnableTrustet
        self.allowedRoles = pAllowedRoles
        