import pandas as pd
import io
from tsfresh.utilities.dataframe_functions import make_forecasting_frame
from tsfresh.utilities.dataframe_functions import impute
from tsfresh import extract_features
from sklearn.ensemble import RandomForestRegressor
import tqdm
import numpy as np
from numpy import dtype
from S3Repository import S3Repository


class ModelManager:
    def __init__(self):
        self.repository = S3Repository()
        self.key = ''

    def upload_data(self, name, file):
        numeric_cols = []
        enum_cols = []
        numeric_types = [dtype('int32'), dtype('int64'), dtype('float'), dtype('float64')]

        crime_data = pd.read_csv(file, encoding="ISO-8859-1")
        file.seek(0)

        # identify numeric and enum columns
        for key in crime_data.keys():
            # column is numeric type
            if numeric_types.count(crime_data.dtypes[key]) > 0:
                numeric_cols.append(key)
            else:
                enum_cols.append(key)

        # add file to s3
        self.key = self.repository.data_directory + name
        print(self.key)
        self.repository.write_file(self.key, file)

        return {
            "numericCols": numeric_cols,
            "enumCols": enum_cols
        }

    def generate_model(self, prediction_year):
        # get file from S3
        self.key = 'Dev_tenant/data/911_Police_Calls'
        file = self.repository.get_file(self.key)
        crime_data = pd.read_csv(io.BytesIO(file.read()))

        # select columns needed for prediction
        crime_data = crime_data[['CallDateTime', 'PoliceDistrict']]
        # crime_data = crime_data[:500]
        # drop rows with null values
        columns = crime_data.columns.tolist()
        for i in columns:
            rows_with_null_values = crime_data[crime_data[i].isnull()].index
            crime_data = crime_data.drop(rows_with_null_values, axis=0)

        # convert callDateTime column to pandas datetime format
        crime_data['CallDateTime'] = pd.to_datetime(crime_data['CallDateTime'])

        # create columns Day, Week, Month, Year from CallDateTime column
        day_of_week = crime_data['CallDateTime'].dt.dayofweek
        week = crime_data['CallDateTime'].dt.week
        month = crime_data['CallDateTime'].dt.month
        year = crime_data['CallDateTime'].dt.year

        crime_data['Day'] = day_of_week
        crime_data['Week'] = week
        crime_data['Month'] = month
        crime_data['Year'] = year

        # data for number of crimes per week per PoliceDistrict
        crimes_per_week_data = self.time_series_data_creation('Week', crime_data)

        # generate time series forecasting frame for each PoliceDistrict
        districts = set(crimes_per_week_data['PoliceDistrict'])
        forecasting_frames = self.create_forecasting_frame(crimes_per_week_data, districts)

        # Extract time series features from forecasting frame
        ts_features = self.extract_time_series_features(forecasting_frames)

        # generate prediction using ts_features
        results = [[np.NaN] * len(ts_features[0][1]) for i in range(len(ts_features))]

        isp = 10   # index of where to start the predictions
        assert isp > 0

        index = 0
        for i in ts_features:
            model = RandomForestRegressor()
            for j in tqdm.tqdm(range(isp, len(i[1]))):
                model.fit(i[0].iloc[:j], i[1][:j])
                results[index][j] = model.predict(i[0].iloc[j, :].values.reshape((1, -1)))[0]
            index += 1

        print(results[0])
        # creating prediction dataFrame
        columns = [district for district in districts]
        index = [i for i in range(len(results[0]))]
        predictions = pd.DataFrame(columns=columns, index=index)

        for i in range(len(results)):
            predictions[columns[i]] = results[i]

        # add predictions to s3 repository
        key = self.repository.predictions_directory + 'Prediction'+prediction_year
        self.repository.write_file(key, predictions.to_csv(index=False))

        return "Model generated successfully"

    def create_forecasting_frame(self, data, districts):
        forecasting_frames = []

        for district in districts:
            temp_shift, temp_y = make_forecasting_frame(
                data[data['PoliceDistrict'] == district]['NoOfCrimes'],
                kind="crimes", max_timeshift=20, rolling_direction=1)

            forecasting_frames.append([temp_shift, temp_y])

        return forecasting_frames

    def extract_time_series_features(self, forecasting_frames):
        ts_features = []

        for i in forecasting_frames:
            x = extract_features(i[0], column_id="id", column_sort="time", column_value="value",
                                 impute_function=impute, show_warnings=False)

            ts_features.append([x, i[1]])

        # remove constant features
        for i in ts_features:
            i[0] = i[0].loc[:, i[0].apply(pd.Series.nunique) != 1]

        # add a lag of 1
        for i in ts_features:
            i[0]["feature_last_value"] = i[1].shift(1)

        # drop first row with null value created due to lag
        for i in ts_features:
            i[0] = i[0].iloc[1:, ]
            i[1] = i[1].iloc[1:]

        return ts_features

    def time_series_data_creation(self, group_by_parameter, crime_data):
        parameters = {
            'Year': 'Month',
            'Month': 'Week',
            'Week': 'Day',
            'Day': 'Error'}

        lower_group_by_parameter = parameters[group_by_parameter]

        if lower_group_by_parameter == 'Error':
            raise AttributeError('group_by_parameter cannot be "Day"')

        # create a set of all PoliceDistrict
        police_districts = set(crime_data['PoliceDistrict'])

        time_series_data = []

        for district in police_districts:
            for week_num, week_value in crime_data[crime_data['PoliceDistrict'] == district].groupby(group_by_parameter):
                total_weekly_crimes = len(week_value)
                daily_crimes = [0] * 7
                for day_num, day_value in week_value.groupby(lower_group_by_parameter):
                    total_daily_crime = len(day_value)
                    daily_crimes[day_num] = total_daily_crime

                time_series_data.append([district, week_num] + daily_crimes + [total_weekly_crimes])

        time_series_data = pd.DataFrame(time_series_data, columns=['PoliceDistrict', 'Week_Number', 'Monday', 'Tuesday',
                                                                   'Wednesday', 'Thursday', 'Friday', 'Saturday',
                                                                   'Sunday', 'NoOfCrimes'])
        return time_series_data



