import datetime as dt
from zoneinfo import ZoneInfo
from briefing import decode_subject, item, load_tasks, render

def test_email_header():
    assert decode_subject('=?utf-8?b?VGVzdCDigJQ=?=') == 'Test —'

def test_render_escapes_untrusted_news():
    now=dt.datetime(2026,11,9,6,tzinfo=ZoneInfo('America/Chicago'))
    payload={'tasks':[], 'calendar':[], 'mail':[], 'research':[], 'futures':[],
             'weather':[], 'news':{'Example':[item('<script>alert(1)</script>','javascript:alert(1)')]},
             'insight':None}
    output=render(payload,now,{'official_links':[]})
    assert '<script>' not in output
    assert 'href="javascript:' not in output
    assert '&lt;script&gt;' in output

def test_tasks_loaded():
    now=dt.datetime(2026,11,9,tzinfo=ZoneInfo('America/Chicago'))
    assert load_tasks(now)
