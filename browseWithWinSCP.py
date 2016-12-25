import sublime_plugin, sublime, subprocess, os, sys
from .dirConfig import getConfig, copyDefaultConfig

isInitialized = False
startWinscpCommand = ""
configName = 'sftp-config.json'

def init():
	# Init settings
	settings = sublime.load_settings('WinSCP.sublime-settings');
	winscpExe = settings.get('winscpExe') or "winSCP"
	print("Load settings: "+winscpExe)

	# Generate default settings
	if (not settings.has('winscpExe')):
		print("No Setting Found")
		if sys.platform.startswith('win'):
				try:
					winscpExe = '"' + os.environ['ProgramFiles'] + '\WinSCP\WinSCP.exe' + '"'
					winscpExe = '"' + os.environ['ProgramFiles(x86)'] + '\WinSCP\WinSCP.exe' + '"'
				except KeyError:
					pass
		settings.set('winscpExe', winscpExe)
		sublime.save_settings('WinSCP.sublime-settings')

	# Genetate winscp command
	startWinscpCommand = winscpExe + ' {type}://"{user}":"{password}"@{host}:{port}"{remote_path}" /rawsettings LocalDirectory="{local_path}"'
	if sys.platform == 'darwin':
		startWinscpCommand = "/Applications/Wine.app/Contents/Resources/bin/wine  " + startWinscpCommand

	isInitialized = True
	return startWinscpCommand

class browse_with_winscpCommand(sublime_plugin.WindowCommand):
	def run(self, edit = None):
		if not isInitialized:
			startWinscpCommand = init()

		print("winscp: "+startWinscpCommand)
		try:
			conf = getConfig(configName, True)
		except AttributeError:
			print("No method found for getConfig()")
		if conf is not None:
			subprocess.Popen(startWinscpCommand.format(**conf), shell=True)
			print ("command is:"+startWinscpCommand)
		else:
			if(sublime.ok_cancel_dialog("No config file found.\nWould you like to create a default config?")):
				copyDefaultConfig(configName)

class send_with_winscpCommand(sublime_plugin.WindowCommand):
	def run(self, edit = None):
		if not isInitialized:
			startWinscpCommand = init()

		print("winscp: "+startWinscpCommand)
		try:
			conf = getConfig(configName, False)
		except AttributeError:
			print("No method found for getConfig()")
		if conf is not None:
			remoteLocString = sublime.active_window().active_view().file_name()
			print(remoteLocString)
			for currentFolder in sublime.active_window().folders():
				if (remoteLocString.startswith(currentFolder)):
					print ("Found a prefix with "+currentFolder)
					remoteLocString = remoteLocString[len(currentFolder)+1:]
				print(remoteLocString)

			remoteLocString = remoteLocString.replace('\\', '/')
			sendCommandString = '/console /command "put '+sublime.active_window().active_view().file_name()+' '+remoteLocString+'"'

			subprocess.Popen(startWinscpCommand.format(**conf)+" "+sendCommandString, shell=True)
			print ("command is:"+startWinscpCommand.format(**conf)+" "+sendCommandString)
		else:
			if(sublime.ok_cancel_dialog("No config file found.\nWould you like to create a default config?")):
				copyDefaultConfig(configName)
