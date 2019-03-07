import sublime
import sublime_plugin
import datetime


class _TriageEntryCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return self.view.match_selector(0, 'text.triage')

    def expand_to_triage_entry(self, region):
        begin = region.begin()
        end = region.end()

        prev_begin = None
        while begin != prev_begin:
            prev_begin = begin
            begin = self.view.find_by_class(begin, False, sublime.CLASS_LINE_START)
            if self.view.match_selector(begin, 'meta.entry.triage'):
                break

        prev_end = None
        while end != prev_end:
            prev_end = end
            end = self.view.find_by_class(end, True, sublime.CLASS_LINE_END)
            if self.view.match_selector(self.view.line(end).begin(), 'meta.entry.triage'):
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


class ResolveTriageEntryCommand(_TriageEntryCommand):
    def is_enabled(self):
        if not super(ResolveTriageEntryCommand, self).is_enabled():
            return False

        return self.view.file_name() is not None

    def description(self):
        return 'Resolve triage entry'

    def run(self, edit):
        triage_path = self.view.file_name()

        import os.path
        archive_path = '../.triage/%s' % datetime.datetime.utcnow().strftime('%Y%m%d')
        archive_file = os.path.normpath(os.path.join(triage_path, archive_path))

        selections = self.view.sel()
        entries = [self.expand_to_triage_entry(selection) for selection in selections]
        selections.clear()
        entries = sorted(entries, key=lambda entry: entry.a)
        entry_text = [
            self.view.substr(entry)
            for entry in entries
        ]

        os.makedirs(os.path.dirname(archive_file), exist_ok=True)
        with open(archive_file, 'a') as f:
            for entry in entry_text:
                f.write(entry)
                f.write('    Marked as resolved at %s\n' % (datetime.datetime.utcnow().strftime('%Y%m%d %H:%M:%S')))

        for entry in reversed(entries):
            self.view.erase(edit, entry)

        self.view.run_command('save')
