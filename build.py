import os.path
import re
import subprocess
import sys

USER_AGENTS = ['Chrome', 'Edge', 'Firefox', 'Safari']


def error(msg):
	print('Error: %s' % (msg))
	sys.exit(1)

class Parser():
	"""Parser for uievents-key spec."""

	def __init__(self):
		self.in_table = False

		self.key = None
		self.opt = ''
		self.desc = ''
		self.is_dup = False

		# Only used for IMPL tables
		self.in_impl_table = False
		self.impl_info = {}
		self.impl_notes = ''
		self.impl_section = False
		self.impl_section_name = ''

	def table_row(self):
		if self.key == None:
			return ''

		req = "Yes"
		if self.opt:
			req = "No"
		if self.is_dup:
			return (
				'<tr><td class="key-table-key"><code class="key">"%s"</code></td>\n'
    			'<td class="key-table-required">%s</td>'
				'<td>%s</td></tr>\n') % (self.key, req, self.desc)

		return (
			'<tr>'
			'<td class="key-table-key"><code class="key" id="key-%s">"%s"</code></td>\n'
			'<td class="key-table-required">%s</td>'
			'<td>%s</td></tr>\n') % (self.key, self.key, req, self.desc)

	def table_row_impl(self):
		if self.impl_section:
			return '<tr><td style="background-color: #B9C9FE" colspan="6">%s</td></tr>\n' % self.impl_section_name

		if self.key == None:
			return ''

		result = '<tr><td class="key-table-key">'
		if self.nolink:
			if self.key == 'Space':
				result += '<code class="key">" "</code>'
			else:
				keys = self.key.split('-')
				result += '...'.join(['<code class="key">"%s"</code>' % key for key in keys])
		else:
			result += '<a href="https://w3c.github.io/uievents-key/#key-%s">' % self.key
			result += '<code class="key">"%s"</code>' % self.key
			result += '</a>'
		result += '</td>\n'
		for ua in USER_AGENTS:
			value = self.impl_info[ua]
			data = ''
			if value == 'Y':
				data = '<span class="key-impl-yes">Pass</span>'
			elif value == 'F':
				data = '<span class="key-impl-no">Fail</span>'
			elif value == '?':
				data = '<span>?</span>'
			else:
				print("ERROR processing impl table:", value)
				data = '<span>?</span>'
			result += '<td class="key-impl-data">%s</td>' % (data)
		notes = self.impl_notes
		if notes == None:
			notes = ''
		result += '<td>%s</td>' % notes
		result += '</tr>\n'
		return result

	def process_text(self, desc):
		has_newline = False
		if desc[-1:] == '\n':
			has_newline = True
		
		m = re.match(r'^(.*)CODE{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="code">"' + name + '"</code>' + post

		m = re.match(r'^(.*)KEY{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = '%s<code class="key">"<a href="#key-%s">%s</a>"</code>%s' % (pre, name, name, post)

		m = re.match(r'^(.*)KEY_NOLINK{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = '%s<code class="key">"%s"</code>%s' % (pre, name, post)

		m = re.match(r'^(.*)KEYCAP{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="keycap">' + name + '</code>' + post

		m = re.match(r'^(.*)GLYPH{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="glyph">"' + name + '"</code>' + post

		m = re.match(r'^(.*)UNI{(.+?)}(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			if name[0:2] != 'U+':
				error('Invalid Unicode value (expected U+xxxx): %s\n' % name)
			desc = pre + '<code class="unicode">' + name + '</code>' + post

		m = re.match(r'^(.*)(KEYCODE_[A-Z0-9_]+)(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="android">' + name + '</code>' + post

		m = re.match(r'^(.*)(APPCOMMAND_[A-Z0-9_]+)(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="appcommand">' + name + '</code>' + post

		m = re.match(r'^(.*)(VK_[A-Z0-9_]+)(.*)$', desc)
		if m:
			pre = self.process_text(m.group(1))
			name = m.group(2)
			post = self.process_text(m.group(3))
			desc = pre + '<code class="vk">' + name + '</code>' + post

		if has_newline and desc[-1:] != '\n':
			desc += '\n'
		return desc

	def process_line(self, line):
		m = re.match(r'^.*KEY(_OPT)? (\w+)\s*(.*)$', line)
		if m:
			# Write out previous key.
			result = self.table_row()
			self.opt = m.group(1)
			self.key = m.group(2)
			self.desc = self.process_text(m.group(3))
			self.is_dup = False
			return result

		m = re.match(r'^.*KEY_DUP(_OPT)? (\w+)\s*(.*)$', line)
		if m:
			result = self.table_row()
			self.opt = m.group(1)
			self.key = m.group(2)
			self.desc = self.process_text(m.group(3))
			self.is_dup = True
			return result

		m = re.match(r'^.*BEGIN_KEY_TABLE ([a-z0-9-]+)', line)
		if m:
			self.key = None
			self.in_table = True
			name = m.group(1)
			return (
				'<table id="key-table-%s" class="data-table full-width">\n'
				'<thead><tr>'
				'<th style="width:20%%">[=key attribute value=]</th>'
				'<th style="width:10%%">Required</th>'
				'<th style="width:70%%">Typical Usage (Non-normative)</th>'
				'</tr></thead>\n'
				'<tbody>\n') % name

		m = re.match(r'^.*END_KEY_TABLE', line)
		if m:
			result = self.table_row()
			self.key = None
			self.in_table = False
			return result + '</tbody></table>\n'

		pattern = r'^\s*KEY_IMPL(?P<nolink>_NOLINK)? (?P<key>[\w-]+)'
		for ua in USER_AGENTS:
			pattern += r'\s+(?P<%s>[YF\?])' % ua
		pattern += r'\s*(?P<Notes>\w.*)?$'
		m = re.match(pattern, line)
		if m:
			# Write previous row.
			result = self.table_row_impl()
			self.key = m.group('key')
			self.nolink = m.group('nolink')
			self.impl_info = {}
			self.impl_section = False
			for ua in USER_AGENTS:
				self.impl_info[ua] = m.group(ua)
			self.impl_notes = m.group('Notes')
			return result

		m = re.match(r'^\s*KEY_IMPL_SECTION (.+)$', line)
		if m:
			result = self.table_row_impl()
			self.key = None
			self.impl_section = True
			self.impl_section_name = m.group(1)
			return result

		m = re.match(r'^\s*BEGIN_KEY_IMPL_TABLE ([a-z0-9-]+)', line)
		if m:
			self.key = None
			self.in_impl_table = True
			name = m.group(1)
			header = '<thead><tr><th>[=key attribute value=]</th>'
			for ua in USER_AGENTS:
				header += '<th class="key-impl-data">%s</th>' % ua
			header += '<th>Notes</th></tr></thead>\n'
			return (
				'<table id="key-table-%s" class="data-table full-width">\n'
				'%s'
				'<tbody>\n') % (name, header)

		m = re.match(r'^\s*END_KEY_IMPL_TABLE', line)
		if m:
			result = self.table_row_impl()
			self.key = None
			self.in_impl_table = False
			return result + '</tbody></table>\n'

		if self.in_table:
			self.desc += self.process_text(line)
			return ''

		if self.in_impl_table:
			m = re.match(r'^(\s*)(<!--.+-->)?(\s*)$', line)
			if m:
				return ''
			print('*** ERROR *** unrecognized line in IMPL table: ' + line)
			return ''
			
		return self.process_text(line)

	def process(self, src, dst):
		if not os.path.isfile(src):
			error('File "%s" doesn\'t exist' % src)

		try:
			infile = open(src, 'r')
		except IOError as e:
			error('Unable to open "%s" for reading: %s' % (src, e))

		try:
			outfile = open(dst, 'w')
		except IOError as e:
			error('Unable to open "%s" for writing: %s' % (dst, e))

		for line in infile:
			new_line = self.process_line(line)
			outfile.write(new_line)

		outfile.close()
		infile.close()

def main():
	files = [
		['index-source.txt', 'index.bs'],
		['impl-report.txt', 'impl-report.bs'],
	]
	
	# Generate the full bikeshed file.
	parser = Parser()
	for f in files:
		src = f[0]
		dst = f[1]
		
		print('Pre-processing %s -> %s' % (src, dst))
		parser.process(src, dst)

		print('Bikeshedding %s...' % dst)
		subprocess.call(["bikeshed", "spec", dst])

if __name__ == '__main__':
	main()
