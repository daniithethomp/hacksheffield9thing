import dataframes as df
import pandas as pd

def driver_standing_over_time(driver):
    drivers_df = df.drivers_df()
    driver_id = (drivers_df)[drivers_df['Full Name'] == driver]['driverId'].iloc[0]
    driver_standing_frame = df.driver_standings_df
    driver_standing_frame = driver_standing_frame[driver_standing_frame['raceId'] != 355]
    driver_specific_standings = driver_standing_frame[driver_standing_frame['driverId'] == driver_id]
    driver_specific_standings = driver_specific_standings.join(df.races_df(), on='raceId', how="left", lsuffix='l', rsuffix='r')
    driver_standing_per_year = driver_specific_standings.loc[driver_specific_standings.groupby('year')['round'].idxmax()]
    driver_standing_per_year['year'] = driver_standing_per_year['year'].astype(int).astype(str)
    return driver_standing_per_year

def constructor_standings_over_time(constructor):
    constructor_df = df.constructors_df
    constructor_id = (constructor_df)[constructor_df['name'] == constructor]['constructorId'].iloc[0]
    constructor_standing_frame = df.constructor_standings_df
    constructor_specific_standings = constructor_standing_frame[constructor_standing_frame['constructorId'] == constructor_id]
    constructor_specific_standings = constructor_specific_standings.join(df.races_df(), on='raceId', lsuffix='l', rsuffix='r')
    constructor_standing_per_year = constructor_specific_standings.loc[constructor_specific_standings.groupby('year')['round'].idxmax()]
    return constructor_standing_per_year

def driver_wins_over_time(driver):
    drivers_df = df.drivers_df()
    driver_id = (drivers_df)[drivers_df['Full Name'] == driver]['driverId'].iloc[0]
    driver_wins_frame = df.driver_standings_df
    driver_specific_wins = driver_wins_frame[driver_wins_frame['driverId'] == driver_id]
    driver_specific_wins = driver_specific_wins.join(df.races_df(), on='raceId', lsuffix='l', rsuffix='r')
    driver_wins_per_year = driver_specific_wins[driver_specific_wins['position'] == 1].groupby('year').size()
    return driver_wins_per_year

def race_data(race, dataframe):
    raceId = (df.races_df())[(df.races_df())['Race Identifier'] == race]['raceId'].iloc[0]
    raceRow = dataframe[dataframe['raceId'] == raceId]
    return raceRow

def best_pit_stop_per_race(race):
    raceRow = race_data(race, df.pit_stop_df)
    if raceRow.empty:
        raise Exception("No pit stops recorded")
    else:
        best_pit_stop = raceRow.loc[raceRow['duration'].idxmin()]
        driver_info = df.drivers_df()[df.drivers_df()['driverId'] == best_pit_stop['driverId']]
        best_pit_stop = pd.merge(best_pit_stop.to_frame().T, driver_info, on='driverId')
        best_pit_stop = best_pit_stop.rename(columns={'duration': 'Pit Duration', 'Full Name': 'Driver'})        
        return best_pit_stop[['Pit Duration', 'Driver']]

def lap_times(race):
    raceRow = race_data(race, df.results_df)
    if raceRow.empty:
        raise Exception("No fastest lap times recorded")
    else:
        best_lap_time = raceRow.loc[raceRow['fastestLapTime'].idxmin()]
        best_lap_time['fastestLapTime'] = best_lap_time['fastestLapTime'].replace("\\N", "No lap time recorded")
        driver_info = df.drivers_df()[df.drivers_df()['driverId'] == best_lap_time['driverId']]
        best_lap_time = pd.merge(best_lap_time.to_frame().T, driver_info, on='driverId')
        best_lap_time = best_lap_time.rename(columns={'fastestLapTime': 'Lap Time', 'Full Name': 'Driver'})        
        return best_lap_time[['Lap Time', 'Driver']]

def race_results(race):
    raceRow = race_data(race, df.results_df)
    if raceRow.empty:
        raise Exception("No race results recorded")
    else:
        results = raceRow[['driverId', 'number', 'position', 'points', 'time']]
        results['time'] = results['time'].replace("\\N", "No time")
        results['position'] = results['position'].replace("\\N", "No position")
        driver_info = df.drivers_df()[['driverId', 'Full Name']]
        results = pd.merge(results, driver_info, on='driverId').drop(columns=['driverId'])
        results['points'] = results['points'].astype(int).astype(str)
        results = results.rename(columns={'Full Name': 'Driver', 'number': 'Driver Number', 'position': 'Position', 'points':'Points', 'time': 'Time'})
        return results[['Driver', 'Driver Number', 'Position', 'Points', 'Time']]

def get_constructor_id(constructor_name):
    return (df.constructors_df)[df.constructors_df['name'] == constructor_name]['constructorId'].iloc[0]


def get_circuit_id(circuit_name):
    return (df.circuit_df)[df.circuit_df['name'] == circuit_name]['circuitId'].iloc[0]

# Will get the points earned by a constructor (at a given circuit) over time
def constructor_results_over_time_per_circuit(constructor_name, circuit_name):
    # Get all race results for that constructor
    results = df.constructor_results_df[df.constructor_results_df['constructorId'] == get_constructor_id(constructor_name)]
    
    # Join race table so can query year, then filter by circuit
    results = results.join(df.races_df(), on='raceId', lsuffix='', rsuffix='_race')
    results = results[results['circuitId'] == get_circuit_id(circuit_name)]

    # Join circuit stats
    results = results.join(df.circuit_df, on='circuitId', lsuffix='', rsuffix='_circuit')

    # Race results for that race, and that constructor
    constructor_results_per_year = results.loc[results.groupby('year')['round'].idxmax()]
    constructor_results_per_year['year'] = constructor_results_per_year['year'].astype(int).astype(str)
    return constructor_results_per_year

def convert_column_to_percent(column_name, dataframe, negate=False):
    max_val = dataframe.loc[dataframe[column_name].idxmax()]
    dataframe.assign(Percentage = lambda x: (x[column_name] /max_val * 100))
    return dataframe

# will get the points earned by a constructor over that year
def constructor_results_across_circuits_over_year(constructor_name, year):
    # Get all race results for that constructor
    results = df.constructor_results_df[df.constructor_results_df['constructorId'] == get_constructor_id(constructor_name)]

    # Join race table to query year, then filter by year
    results = results.join(df.races_df_unsorted(), on='raceId', lsuffix='', rsuffix='_race')

    results = results[results['year'] == year]

    # Join circuit stats
    results = results.join(df.circuit_df, on='circuitId', lsuffix='', rsuffix='_circuit')

    # Race results for that race, and that constructor
    constructor_results_per_year = results.sort_values("round")
    return constructor_results_per_year