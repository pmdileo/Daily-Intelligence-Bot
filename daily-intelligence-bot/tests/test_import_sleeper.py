from import_sleeper import render_report

def test_report_has_team_and_starter():
    report=render_report([{'league':'Example League','league_id':'123','roster_id':1,'players':[{'id':'1','name':'Example Player','position':'QB','team':'KC','injury_status':''}],'starters':['1'],'reserve':[],'taxi':[]}], 'demo',2026)
    assert 'Example League' in report
    assert 'Example Player' in report
    assert 'Starter' in report
