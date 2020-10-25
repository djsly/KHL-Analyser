from nhlpy import player
from datetime import datetime
from csv import DictReader,DictWriter

def get_player_info(player_id):
    player_info = player.Player(player_id).info()

    current_age = ""
    position_type = ""

    active = player_info["people"][0]["active"]
    roster_status = player_info["people"][0]["rosterStatus"]

    if active:
        current_age = player_info["people"][0]["currentAge"]
        position_type = player_info["people"][0]["primaryPosition"]["type"]

    return {"age":current_age, "active":active, "roster":roster_status, "position":position_type}

def get_player_seasons_stat(player_id, starting_year):
    current_year = datetime.now().year
    #print("Getting stats for {} for the last {} years".format(player_id, current_year - starting_year))

    stats = {}
    for i in range(starting_year, current_year+1): 
        #print("retreiving stats {}-{}".format(i, i+1))
        player_stats = player.Player(player_id).season(i, i+1)
        stats[str(i)] = player_stats
    return stats

def print_key_stats_per_years(players_stats):
    merged_data = []
    for name, data in players_stats.items():
        entry = {}
        entry['name'] = name
        entry['salary'] = data["info"]["salary"]
        entry['active'] = data["info"]["active"]
        entry['roster'] = data["info"]["roster"]
        entry['age'] = data["info"]["age"]
        entry['position'] = data["info"]["position"]
        entry['owner'] = data["info"]["owner"]

        print("\n{}:\n\tactive({})\n\troster({})\n\tsalary({})\n\tage({})\n\tposition({})\n\towner({})".format(entry['name'], entry['active'], entry['roster'], entry['salary'], entry['age'], entry['position'], entry['owner']))
        print("\tStats:\n\t\t\tgames\tpoints\tpts/g\tcost/pts[M]")
        if entry['active']:
            for year, stats in data["stats"].items():
                if year == "2020":
                    #print("Skipping 2020 since is hasn't started")
                    #below array indexing breaks when no data (e.g. on started year)
                    continue
                #print("DEBUG (stats): {}".format(stats))
                stats_value = stats.get("stats", [{}])
                splits_value = stats_value[0].get("splits", [{}]) if len(stats_value) > 0 else [{}]
                stat =  splits_value[0].get("stat", {}) if len(splits_value) > 0 else {}
                #print("DEBUG (stat): {}".format(stat))
                points = stat.get("points", 0)
                games = stat.get("games", 0)  
                points_per_game = points/games if games != 0 else 0
                cost_per_point = float(entry['salary'])/points if points != 0 else 0
                entry['{}-games'.format(year)] = games
                entry['{}-points'.format(year)] = points
                entry['{}-ppg'.format(year)] = points_per_game
                entry['{}-cpg'.format(year)] = cost_per_point
                print("\t\t{}:\t{}\t{}\t{:.2f}\t{:.4f}".format(year, games, points, points_per_game, cost_per_point))

        merged_data.append(entry)

    return merged_data

def export_to_csv(merged_data): 
    with open('export.csv', 'w', newline='') as csvfile:
        fieldnames = merged_data[0].keys()
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in merged_data:
            writer.writerow(entry)

if __name__ == "__main__":
    with open('player-id-mapping.csv', newline='') as csvfile:
        reader = DictReader(csvfile)

        players_stats = {}
        for row in reader:
            data = {}
            print("Processing: {}".format(row["name"]))
            data["info"] = (get_player_info(row["id"]))
            data["info"]["salary"] = row["salary"]
            data["info"]["owner"] = row["owner"]
            data["stats"] = (get_player_seasons_stat(row["id"], 2017))
            players_stats[row["name"]] = data

    merged_data =print_key_stats_per_years(players_stats)
    export_to_csv(merged_data)


