from unittest.mock import patch
from sleeper_integration import football_rosters, basketball_rosters, player_feed_queries

def test_nfl_team_identification():
    responses = {
        '/user/demo': {'user_id':'u1'},
        '/user/u1/leagues/nfl/2026': [{'league_id':'l1','name':'Demo League'}],
        '/players/nfl': {'p1':{'full_name':'Example Football Player','team':'KC','position':'QB'}},
        '/league/l1/rosters': [{'owner_id':'different','players':[]}, {'owner_id':'u1','roster_id':4,'players':['p1'],'starters':['p1']}]
    }
    with patch('sleeper_integration.api',side_effect=lambda path: responses[path]):
        result=football_rosters('demo',2026)
    assert result[0]['players'][0]['name']=='Example Football Player'
    assert result[0]['roster_id']==4

def test_league_restriction():
    responses={'/user/demo':{'user_id':'u1'}, '/user/u1/leagues/nfl/2026':[{'league_id':'l1'}]}
    with patch('sleeper_integration.api',side_effect=lambda path: responses[path]):
        assert football_rosters('demo',2026,['other'])==[]

def test_player_searches():
    fake={'nfl':[{'players':[{'name':'Example Football Player'}]}], 'nba':[]}
    assert 'Example Football Player' in player_feed_queries(fake,'nfl')[0]
