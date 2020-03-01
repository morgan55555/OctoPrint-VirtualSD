# coding=utf-8
from __future__ import absolute_import

__author__ = "Alex Morgan <alxmrg55@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2020 Alex Morgan - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.settings import settings
from os import path, remove, errno, sep
from shutil import copyfile
from threading import Thread
from time import time

class VirtualsdPlugin(octoprint.plugin.SettingsPlugin,
					  octoprint.plugin.AssetPlugin,
					  octoprint.plugin.TemplatePlugin):

	def __init__(self):
		self.sdcardUploadReplace = False
		self.sdcardRemoveReplace = False
		self.sdDirectoryByOctoprint = False
		self.sdDirectory = ""
	
	def get_settings_version(self):
		return 1
	
	def on_settings_initialized(self):
		self.sdcardUploadReplace = self._settings.get_boolean(["sdcardUploadReplace"])
		self._logger.debug("Virtual SD card support enabled: %s" % self.sdcardUploadReplace)
		
		self.sdcardRemoveReplace = self._settings.get_boolean(["sdcardRemoveReplace"])
		self._logger.debug("SD card replace support enabled: %s" % self.sdcardRemoveReplace)
		
		self.sdDirectoryByOctoprint = self._settings.get_boolean(["sdDirectoryByOctoprint"])
		self._logger.debug("Set directory by Octoprint upload folder: %s" % self.sdDirectoryByOctoprint)
		
		if self.sdDirectoryByOctoprint:
			self.sdDirectory = settings().getBaseFolder("uploads", check_writable=False)
		else:
			self.sdDirectory = self._settings.get(["sdDirectory"])
		self._logger.debug("Virtual SD path: %s" % self.sdDirectory)

	def get_settings_defaults(self):
		sdDirectory = settings().getBaseFolder("uploads", check_writable=False)
		
		return dict(
			sdcardUploadReplace = True,
			sdcardRemoveReplace = True,
			sdDirectoryByOctoprint = True,
			sdDirectory = sdDirectory,
		)
	
	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		self.on_settings_initialized()
	
	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=True)
		]

	def get_assets(self):
		return dict(
			js=["js/virtualsd.js"],
		)

	def get_update_information(self):
		return dict(
			virtualsd=dict(
				displayName="Virtualsd Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="morgan55555",
				repo="OctoPrint-VirtualSD",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/morgan55555/OctoPrint-VirtualSD/archive/{target_version}.zip"
			)
		)
	
	def hook_gcode_queuing(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if self.sdcardRemoveReplace:
			if gcode:
				if gcode == "M30":					
					filename = ""
					
					try:
						filename = cmd.split(None, 1)[1]
					except IndexError:
						comm_instance._log("Filename required")
						return (None,)
					
					filename = filename.strip()
					filename = filename.lower()
					
					if filename.startswith("/"):
						filename = filename[1:]
					
					filepath = path.join(self.sdDirectory, filename)
					
					try:
						remove(filepath)
					except OSError as e:
						if e.errno == errno.ENOENT:
							comm_instance._log("File '%s' not found!" % filename)
						else:
							comm_instance._log("Error when removing file, check logs for info")
							self._logger.error("OS error when removing file: %s" % str(e))
					else:
						comm_instance._log("File %s removed." % filename)
					
					return (None,)
	
	def sd_card_upload_hook(self, printer, descname, sourcepath, start_callback, success_callback, failure_callback, *args, **kwargs):
		if self.sdcardUploadReplace:
			newname = descname.lower()
			start_callback(descname, newname)
			def process():
				start_time = time()
				success = True
				if not self.sdDirectoryByOctoprint:
					try:
						filepath = path.join(self.sdDirectory, newname)
						copyfile(sourcepath, filepath)
					except SameFileError:
						pass
					except Exception as e:
						self._logger.error("Error when copying file: %s" % str(e))
						success = False
				end_time = time()
				elapsed = float("%.2f" % (end_time - start_time))
				if success:
					success_callback(descname, newname, elapsed)
				else:
					failure_callback(descname, newname, elapsed)
				printer.refresh_sd_files()
				
			thread = Thread(target=process)
			thread.daemon = True
			thread.start()
			
			return newname

__plugin_name__ = "Virtualsd Plugin"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = VirtualsdPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.hook_gcode_queuing,
		"octoprint.printer.sdcardupload": __plugin_implementation__.sd_card_upload_hook,
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

