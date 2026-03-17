import re
import glob
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arecom.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

base_dir = os.path.abspath(os.path.dirname(__file__))
# Search templates relative to project root
pattern = os.path.join(os.path.dirname(base_dir), 'templates', '**', '*.html')

url_names = set()
for path in glob.glob(pattern, recursive=True):
    with open(path, encoding='utf-8') as f:
        txt = f.read()
    for m in re.finditer(r"\{\%\s*url\s+'([^']+)'", txt):
        url_names.add(m.group(1))
    for m in re.finditer(r"\{\%\s*url\s+\"([^\"]+)\"", txt):
        url_names.add(m.group(1))

errors = []
for name in sorted(url_names):
    try:
        reverse(name)
    except NoReverseMatch as e:
        errors.append((name, str(e)))

print('Found URL names:', len(url_names))
print('Reverse errors:', len(errors))
for name, err in errors:
    print('-', name, err)
