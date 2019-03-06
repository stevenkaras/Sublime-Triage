import sublime
import sublime_plugin
import datetime


class _TriageEntryCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return 'text.triage' in self.view.scope_name(0).split()

    def expand_to_triage_entry(self, region):
        begin = region.begin()
        end = region.end()

        prev_begin = None
        while begin != prev_begin:
            prev_begin = begin
            begin = self.view.find_by_class(begin, False, sublime.CLASS_LINE_START)
            if 'meta.entry.triage' in self.view.scope_name(begin).split():
                break

        prev_end = None
        while end != prev_end:
            prev_end = end
            end = self.view.find_by_class(end, True, sublime.CLASS_LINE_END)
            if 'meta.entry.triage' in self.view.scope_name(self.view.line(end).begin()).split():
                end = self.view.line(end).begin()
                break

        return sublime.Region(begin, end)


class InsertDateCommand(_TriageEntryCommand):
    def description(self):
        return 'Insert today\'s date'

    def run(self, edit):
        current_date = datetime.datetime.utcnow().strftime('%Y%m%d')
        for selection in self.view.sel():
            self.view.insert(edit, selection.begin(), current_date)


class SelectTriageEntryCommand(_TriageEntryCommand):
    def description(self):
        return 'Select triage entry'

    def run(self, edit):
        selections = self.view.sel()
        entries = [self.expand_to_triage_entry(selection) for selection in selections]
        selections.clear()
        selections.add_all(entries)


class WorkonTriageEntryCommand(_TriageEntryCommand):
    def description(self):
        return 'Move triage entry to top'

    def run(self, edit):
        selections = self.view.sel()
        entries = [self.expand_to_triage_entry(selection) for selection in selections]
        selections.clear()
        entries = sorted(entries, key=lambda entry: entry.a)
        entry_text = [
            self.view.substr(entry)
            for entry in entries
        ]
        for entry in reversed(entries):
            self.view.erase(edit, entry)
        end = 0
        for entry in entry_text:
            end += self.view.insert(edit, 0, entry)

        selections.add(sublime.Region(0, end))
