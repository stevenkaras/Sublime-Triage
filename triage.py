import sublime
import sublime_plugin
import datetime

class InsertDateCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return 'text.triage' in self.view.scope_name(0).split()

    def description(self):
        return 'Insert today\'s date'

    def run(self, edit):
        current_date = datetime.datetime.utcnow().strftime('%Y%m%d')
        for selection in self.view.sel():
            self.view.insert(edit, selection.begin(), current_date)
