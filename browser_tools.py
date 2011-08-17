import os
import re
import urllib
import webbrowser

import sublime, sublime_plugin

browser_file_exts = set(('.html', '.htm', '.css', '.xml'))

# URL regex from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
url_re = re.compile(r"""
(?P<url>                                # Capture 1: entire matched URL
  (?:
    [a-z][\w-]+:                        # URL protocol and colon
    (?:
      /{1,3}                            # 1-3 slashes
      |                                 #   or
      [a-z0-9%]                         # Single letter or digit or '%'
                                        # (Trying not to match e.g. "URI::Escape")
    )
    |                                   #   or
    www\d{0,3}[.]                       # "www.", "www1.", "www2." ... "www999."
    |                                   #   or
    [a-z0-9.\-]+[.][a-z]{2,4}/          # looks like domain name followed by a slash
  )
  (?:                                   # One or more:
    [^\s()<>]+                          # Run of non-space, non-()<>
    |                                   #   or
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
  )+
  (?:                                   # End with:
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
    |                                   #   or
    [^\s`!()\[\]{};:'".,<>?]            # not a space or one of these punct chars
  )
)""", re.VERBOSE | re.MULTILINE)

class open_url_in_selection(sublime_plugin.TextCommand):
    """If the point is on or next to a URL, open it in a browser tab."""

    def run(self, edit):
        url = self.get_url_in_sel()
        if url:
            webbrowser.open_new_tab(url)

    def is_enabled(self):
        return True if self.get_url_in_sel() else False

    def description(self):
        url = self.get_url_in_sel()
        if url:
            return 'Open URL "%s"' % url
        else:
            return 'Open URL'

    def get_url_in_sel(self):
        for region in self.view.sel():
            searchRegion = self.view.line(region)
            paddedRegion = sublime.Region(region.begin() - 1, region.end() + 1)
            for lineRegion in self.view.split_by_newlines(searchRegion):
                line = self.view.substr(lineRegion)
                for match in url_re.finditer(line):
                    span = match.span('url')
                    matchRegion = sublime.Region(span[0] + lineRegion.begin(), span[1] + lineRegion.begin())
                    if paddedRegion.intersects(matchRegion):
                        return match.group('url')


class open_file_in_browser(sublime_plugin.TextCommand):
    """Open the current file in a web browser if it's a valid file type."""

    def run(self, edit):
        file_path = self.get_current_file()
        if file_path:
            url = 'file:' + urllib.pathname2url(file_path)
            webbrowser.open_new_tab(url)

    def is_enabled(self):
        return self.get_current_file() != None

    def get_current_file(self):
        file_path = self.view.file_name()
        if file_path:
            file_path = os.path.abspath(file_path)
            if os.path.isfile(file_path):
                name, ext = os.path.splitext(file_path)
                if ext in browser_file_exts:
                    return file_path
        return None