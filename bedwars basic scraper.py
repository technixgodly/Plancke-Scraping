import requests
from bs4 import BeautifulSoup

def get_bedwars_stats(ign):
    urlheaders = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6218.0 Safari/537.36"
    }
    url = f"https://plancke.io/hypixel/player/stats/{ign}"
    response = requests.get(url, headers=urlheaders)
    
    if response.status_code != 200:
        print(f"Couldnt retrieve data for {ign}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # find the panel
    bedwars_panel = soup.find('div', {'id': 'stat_panel_BedWars'})
    
    if not bedwars_panel:
        print("BedWars stats not found.")
        return
    
    # get table
    table = bedwars_panel.find('table')
    if not table:
        print("BedWars table not found.")
        return
    

    header_rows = table.find_all('tr')
    main_headers = [th.text.strip() for th in header_rows[1].find_all('th')]
    
    
    data = []
    for row in table.find_all('tr')[2:]:  
        cols = row.find_all(['th', 'td'])  
        cols = [col.text.strip().replace('\n', ' ') for col in cols]
        if len(cols) == 11:  
            data.append(cols)
    

    print(
        f"{'Type':<20} {'Normal Kills':<12} {'Normal Deaths':<12} {'Normal K/D':<10} "
        f"{'Final Kills':<12} {'Final Deaths':<12} {'Final K/D':<10} "
        f"{'Wins':<8} {'Losses':<8} {'W/L':<8} {'Beds Broken':<12}"
    )
    
    for row in data:
        print(
            f"{row[0]:<20} {row[1]:<12} {row[2]:<12} {row[3]:<10} "
            f"{row[4]:<12} {row[5]:<12} {row[6]:<10} "
            f"{row[7]:<8} {row[8]:<8} {row[9]:<8} {row[10]:<12}"
        )

if __name__ == "__main__":
    ign = input("Enter the IGN (In-Game Name): ")
    get_bedwars_stats(ign)