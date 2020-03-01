/*
 * View model for OctoPrint-VirtualSD
 *
 * Author: Alex Morgan
 * License: AGPLv3
 */
$(function() {
	function VirtualsdViewModel(parameters) {
		var self = this;
		
		self.settings = parameters[0];
		
        self.onBeforeBinding = function() {
            self.settings = self.settings.settings.plugins.virtualsd;
        };
		
		self.testVirtualSdPathStatus = ko.observable("");
		self.testVirtualSdPathChecked = ko.observable(false);
		self.testVirtualSdPathValid = ko.observable(false);
		
        self.testVirtualSdPathBusy = ko.observable(false);
        self.testVirtualSdPath = function() {
            if (self.testVirtualSdPathBusy()) return;
            self.testVirtualSdPathBusy(true);

            var opts = {
                check_type: "dir",
                check_access: "w",
                allow_create_dir: true,
                check_writable_dir: true
            };
            var path = self.settings.sdDirectory();
			
            OctoPrint.util.testPath(path, opts)
                .done(function(response) {
                    if (!response.result) {
                        if (response.broken_symlink) {
                            self.testVirtualSdPathStatus(gettext("The path is a broken symlink."));
                        } else if (!response.exists) {
                            self.testVirtualSdPathStatus(gettext("The path does not exist and cannot be created."));
                        } else if (!response.typeok) {
                            self.testVirtualSdPathStatus(gettext("The path is not a folder."));
                        } else if (!response.access) {
                            self.testVirtualSdPathStatus(gettext("The path is not writable."));
                        }
                    } else {
                        self.testVirtualSdPathStatus(gettext("The path is valid"));
                    }
					self.testVirtualSdPathChecked(true);
                    self.testVirtualSdPathValid(response.result);
                })
                .always(function() {
                    self.testVirtualSdPathBusy(false);
                });
        };
		
        self.testVirtualSdPathReset = function() {
			self.testVirtualSdPathStatus("");
			self.testVirtualSdPathChecked(false);
			self.testVirtualSdPathValid(false);
        };
		
		
	}

	/* view model class, parameters for constructor, container to bind to
	 * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
	 * and a full list of the available options.
	 */
	OCTOPRINT_VIEWMODELS.push({
		construct: VirtualsdViewModel,
		// ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
		dependencies: [ "settingsViewModel" ],
		// Elements to bind to, e.g. #settings_plugin_virtualsd, #tab_plugin_virtualsd, ...
		elements: [ "#settings_plugin_virtualsd" ]
	});
});
