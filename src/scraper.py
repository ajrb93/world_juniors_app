import pandas as pd
import numpy as np
import os
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from io import StringIO

# PATH CONFIGURATION
DYNAMIC_DIR = 'data/dynamic/Stats_CY'
MASTER_FILE = 'data/dynamic/Stats_CY_Master.csv'
os.makedirs(DYNAMIC_DIR, exist_ok=True)

def get_website(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(3) 
        content = page.content()
        browser.close()
        return content

def extract_schedule_list(year):
    schedule_url_list = []
    soup_file = get_website('https://www.iihf.com/en/events/'+year+'/wm20/schedule')
    soup = BeautifulSoup(soup_file,'html.parser')
    temp_game_url = soup.find_all('a',{'class':'s-hover__link','target':'_blank'})
    for j in range(0,len(temp_game_url)):
        schedule_url_list.append('https://www.iihf.com'+temp_game_url[j]['href'])
    return schedule_url_list

def extract_game_winners(soup):
    game_summary_data = pd.read_html(StringIO(str(soup.find('div',{'class':'s-left-rail-fixed-content'}).find('div',{'class':'s-module-content'}))))[0]
    game_summary_winner = game_summary_data[game_summary_data.TOT == game_summary_data.TOT.max()].teams.values[0]
    game_summary_winning_goal = game_summary_data.TOT.min()+1
    game_goal_scorers_data = (soup.find('div',{'class':'s-left-rail-fixed-content'}).find('div',{'class':'m-scoring'}).
                              find_all('div',{'class':'s-player-name'}))
    game_goal_scorers = []
    for j in range(0,len(game_goal_scorers_data)):
        temp = game_goal_scorers_data[j].text.strip()
        game_goal_scorers.append(temp)
    game_goal_scorers = pd.DataFrame(game_goal_scorers,columns=['name'])
    return game_goal_scorers, game_summary_winner, game_summary_winning_goal

def extract_game_lineups(soup):
    game_lineup_home = []
    game_lineup_data = soup.find('div',{'class':'s-team--home'}).find_all('span',{'class':'s-value'})
    for k in range(0,len(game_lineup_data)): 
        game_lineup_home.append(game_lineup_data[k].text)
    game_lineup_home = pd.DataFrame(game_lineup_home,columns=['data'])
    game_lineup_home['id'] = 1
    game_lineup_home.id = game_lineup_home.id.cumsum() - 1
    game_lineup_home['id2'] = np.round((game_lineup_home.id - 1) / 3,0)
    game_lineup_home.id = game_lineup_home.id % 3
    game_lineup_home = game_lineup_home.pivot(index='id2',columns='id',values='data')
    game_lineup_home['key'] = 1
    game_lineup_home.loc[game_lineup_home[2] == 'GK','Pos'] = 'GK'
    game_lineup_home['Pos_ID'] = game_lineup_home.groupby(game_lineup_home[2]).key.cumsum()
    game_lineup_home.loc[(game_lineup_home[2] == 'D') & (game_lineup_home.Pos_ID % 2 == 1),'Pos'] = 'LD'
    game_lineup_home.loc[(game_lineup_home[2] == 'D') & (game_lineup_home.Pos_ID % 2 == 0),'Pos'] = 'RD'
    game_lineup_home.loc[(game_lineup_home[2] == 'F') & (game_lineup_home.Pos_ID % 3 == 1),'Pos'] = 'LW'
    game_lineup_home.loc[(game_lineup_home[2] == 'F') & (game_lineup_home.Pos_ID % 3 == 2),'Pos'] = 'C'
    game_lineup_home.loc[(game_lineup_home[2] == 'F') & (game_lineup_home.Pos_ID % 3 == 0),'Pos'] = 'RW'
    game_lineup_home.loc[(game_lineup_home[2] == 'D'),'Pos_ID'] = np.round((game_lineup_home.Pos_ID + 0.5) / 2,0)
    game_lineup_home.loc[(game_lineup_home[2] == 'F'),'Pos_ID'] = np.round((game_lineup_home.Pos_ID + 0.67) / 3,0)
    game_lineup_home = game_lineup_home.rename(columns={1:'name'}).drop(columns=[0,2,'key'])
        
    game_lineup_away = []
    game_lineup_data = soup.find('div',{'class':'s-team--away'}).find_all('span',{'class':'s-value'})
    for k in range(0,len(game_lineup_data)): 
        game_lineup_away.append(game_lineup_data[k].text)   
    game_lineup_away = pd.DataFrame(game_lineup_away,columns=['data'])
    game_lineup_away['id'] = 1
    game_lineup_away.id = game_lineup_away.id.cumsum() - 1
    game_lineup_away['id2'] = np.round((game_lineup_away.id - 1) / 3,0)
    game_lineup_away.id = game_lineup_away.id % 3
    game_lineup_away = game_lineup_away.pivot(index='id2',columns='id',values='data')
    game_lineup_away['key'] = 1
    game_lineup_away.loc[game_lineup_away[2] == 'GK','Pos'] = 'GK'
    game_lineup_away['Pos_ID'] = game_lineup_away.groupby(game_lineup_away[2]).key.cumsum()
    game_lineup_away.loc[(game_lineup_away[2] == 'D') & (game_lineup_away.Pos_ID % 2 == 1),'Pos'] = 'LD'
    game_lineup_away.loc[(game_lineup_away[2] == 'D') & (game_lineup_away.Pos_ID % 2 == 0),'Pos'] = 'RD'
    game_lineup_away.loc[(game_lineup_away[2] == 'F') & (game_lineup_away.Pos_ID % 3 == 1),'Pos'] = 'LW'
    game_lineup_away.loc[(game_lineup_away[2] == 'F') & (game_lineup_away.Pos_ID % 3 == 2),'Pos'] = 'C'
    game_lineup_away.loc[(game_lineup_away[2] == 'F') & (game_lineup_away.Pos_ID % 3 == 0),'Pos'] = 'RW'
    game_lineup_away.loc[(game_lineup_away[2] == 'D'),'Pos_ID'] = np.round((game_lineup_away.Pos_ID + 0.5) / 2,0)
    game_lineup_away.loc[(game_lineup_away[2] == 'F'),'Pos_ID'] = np.round((game_lineup_away.Pos_ID + 0.67) / 3,0)
    game_lineup_away = game_lineup_away.rename(columns={1:'name'}).drop(columns=[0,2,'key'])
        
    game_lineups = pd.concat((game_lineup_home,game_lineup_away))
    return game_lineups

def extract_game_stats(soup,url):
    game_data = temp_url_statistics.split('/')[-1].split('-')
    game_data_year = temp_url_statistics.split('/')[5]
    game_data_team = [game_data[1],game_data[3]]
    game_data_id = game_data[0]
    game_statistics = pd.DataFrame()

    for k in range(0,2):
        game_statistics_tables = pd.read_html(StringIO(str(soup.find_all('div',{'class':'m-statistics-table'})[k])))
        game_statistics_tables_skaters = pd.concat((game_statistics_tables[0],game_statistics_tables[1]),axis=1)
        game_statistics_tables_goaltenders = pd.concat((game_statistics_tables[2],game_statistics_tables[3]),axis=1)
        game_statistics_tables = pd.concat((game_statistics_tables_skaters,game_statistics_tables_goaltenders))
        game_statistics_tables = game_statistics_tables[game_statistics_tables.columns
                                                        [~game_statistics_tables.columns.str.contains('Unnamed')]]    
        game_statistics_tables = game_statistics_tables.drop(columns=['avg','svs%'])
        game_statistics_tables['game_id'] = game_data_id
        game_statistics_tables['team'] = game_data_team[k]
        game_statistics_tables['matchup'] = game_data[1]+'-'+game_data[3]
        game_statistics_tables['year'] = game_data_year

        game_statistics = pd.concat((game_statistics,game_statistics_tables))
    return game_statistics

def run_pipeline():
    current_year = '2026'
    schedule_list = extract_schedule_list(current_year)
    schedule_list = [x for x in schedule_list if "playbyplay" in x]

    # Check which games we already have in the dynamic folder
    completed = [x.replace(".csv", "") for x in os.listdir(DYNAMIC_DIR) if ".csv" in x]
    to_process = [url for url in schedule_list if not any(name in url.split('/')[-1] for name in completed)]

    print(f"Found {len(to_process)} new games.")

    for url in to_process:
        try:
            temp_url = url
            temp_url_lineup = temp_url.replace('playbyplay','lineup')
            temp_url_statistics = temp_url.replace('playbyplay','statistics')
            lineups = get_website(temp_url_lineup)
            lineups_soup = BeautifulSoup(lineups,'html.parser')
            if lineups_soup.find('title').text == "IIHF Error page":
                print(url)
                break
            else:
                game_winners, gwgscorer, gwg = extract_game_winners(lineups_soup)
                lineups = extract_game_lineups(lineups_soup)
                stats = get_website(temp_url_statistics)
                stats_soup = BeautifulSoup(stats,'html.parser')
                if stats_soup.find('title').text == "IIHF Error page":
                    print(url)
                    break
                else:
                    stats = extract_game_stats(stats_soup,temp_url_statistics)
                    game_gwg = game_winners.merge(stats[['name','team']])
                    game_gwg = game_gwg[game_gwg.team == gwgscorer.lower()].reset_index(drop=True)
                    game_gwg = game_gwg[game_gwg.index == gwg-1]
                    stats.loc[stats.name == game_gwg.name.values[0],'gwg'] = 1
                    stats = stats.merge(lineups,on='name',how='left')
                    stats = stats.fillna(0)
                    stats.to_csv(f"{DYNAMIC_DIR}/{url.split('/')[-1]}.csv", index=False)
            pass
        except Exception as e:
            print(f"Error processing {url}: {e}")
    all_files = [f"{DYNAMIC_DIR}/{f}" for f in os.listdir(DYNAMIC_DIR) if f.endswith('.csv')]
    if all_files:
        stats_full = pd.concat([pd.read_csv(f) for f in all_files])
        stats_full = stats_full[stats_full.pos != 'GK']
        stats_full['FP'] = (stats_full.g*1.5+ stats_full.a+ stats_full.gwg*3)
        total_spm = stats_full.sog.sum() / (stats_full.game_id.max() * 2 * 60)
        stats_full['minutes'] = stats_full.tot.str.split(':').str[0].astype('int') + stats_full.tot.str.split(':').str[1].astype('int')/60
        stats_full['team_spma'] = (stats_full.groupby(['team','game_id']).sog.transform('sum') / (stats_full.groupby(['team','game_id']).minutes.transform('sum') / 6))
        stats_full['OGS'] = stats_full.g * 0.75 + stats_full.a * 0.625 + stats_full.ts * 0.075
        stats_full['DGS'] = stats_full['+/-'] * 0.15 + (total_spm - stats_full.team_spma) * stats_full.minutes * 0.05
        stats_full.loc[stats_full.pos == 'D','DGS'] *= 1.5
        stats_full.loc[stats_full.pos == 'F','DGS'] *= 0.75
        stats_full['GGS'] = stats_full.svs * 0.1 - stats_full.ga * 0.75
        stats_full.loc[stats_full.pos == 'GK','DGS'] = 0
        stats_full['GS'] = stats_full.OGS + stats_full.DGS + stats_full.GGS
        stats_full = stats_full.drop(columns='team_spma')
        stats_full.to_csv(MASTER_FILE, index=False)
        print(f"Pipeline Complete: {MASTER_FILE} updated.")

def transform_final_dataset():
    dynamic_master_path = 'data/dynamic/Stats_CY_Master.csv'
    if os.path.exists(dynamic_master_path):
        print(f"Loading existing data from {dynamic_master_path}")
        current = pd.read_csv(dynamic_master_path)
    else:
        print("First run: Stats_CY_Master.csv not found. Creating empty template.")
        current = pd.DataFrame(columns=['year','name','game_id'])
    historical = pd.read_csv('data/static/Stats_Historical.csv')
    rosters = pd.read_csv('data/static/Rosters_Full.csv')
    draft = pd.read_csv('data/static/DraftResults.txt',index_col=False) 

    cols_to_drop = ['Pos','Pos_ID','Unnamed: 0.1','Unnamed: 0','tot','shf']
    current = current.drop(columns=[c for c in cols_to_drop if c in current.columns])
    historical = historical.drop(columns=[c for c in historical.columns if 'Unnamed' in c])
    
    current = current[~current.year.isin(historical.year.unique())]
    stats = pd.concat((current, historical))

    rosters = rosters.drop(columns=[c for c in rosters.columns if 'Unnamed' in c])
    stats = stats.merge(rosters, how='left')
    df = stats.merge(draft, how='left')

    df.loc[(~df.fantasyplayer.isna()) & (df.game_start > df.game_id), 'fantasyplayer'] = np.nan 
    df.loc[df.game_start == 0, 'draft_type'] = 'Initial'
    df.loc[(df.game_start >= 25) & ~(df.fantasyplayer.isna()), 'draft_type'] = 'Secondary'
    df = df.fillna('')

    df.to_csv('data/dynamic/Final_Master_Dataset.csv', index=False)
    print("Final visualization dataset created: data/dynamic/Final_Master_Dataset.csv")

if __name__ == "__main__":
    run_pipeline() 
    transform_final_dataset()