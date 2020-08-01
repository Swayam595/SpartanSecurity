import io
import pickle

import pandas as pd
import numpy as np

from numpy import dtype
from sklearn.tree import DecisionTreeClassifier

from Utilities import Utilities
from Model import Model
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import tree
from sklearn.linear_model import Lasso

from S3Repository import S3Repository


class ModelManager:
    
    def __init__(self):
        self.repository = S3Repository()
        self.meta = self.repository.meta
        self.models = []

        # bring the models in memory
        for obj in self.meta["models"]:
            if obj["inMemory"]:
                self.activate_model(obj["name"])

        return

    def upload(self, name, file):
        if any(data['name'] == name for data in self.meta['data']):
            # name already exists
            raise Exception("Dataset already exist. Use different name.")
        else:
            numericCols = []
            enumCols = []
            numeric_types = [dtype('int32'), dtype('int64'), dtype('float'), dtype('float64')]

            # self.auto_data = pd.read_csv('./Data/auto_data.csv', sep=r'\s*,\s*', engine='python')
            # auto_data = pd.read_csv(io.BytesIO(file))
            auto_data = pd.read_csv(file, encoding="ISO-8859-1")
            file.seek(0)

            for key in auto_data.keys():
                # column is numeric type
                if numeric_types.count(auto_data.dtypes[key]) > 0:
                    numericCols.append(key)
                else:
                    enumCols.append(key)

            # add to file to s3
            key = self.repository.data_directory + name
            self.repository.write_file(key, file)

            # add info in metadata file
            self.meta['data'].append({
                "name": name,
                "key": key,
                "numericCols": numericCols,
                "enumCols": enumCols
            })

            self.repository.update_meta(self.meta)

        return {
            "numericCols": numericCols,
            "enumCols": enumCols
        }

    def getMeta(self):
        meta = []
        for obj in self.meta['data']:
            meta.append({
                "name": obj["name"],
                "numericCols": obj["numericCols"],
                "enumCols": obj["enumCols"]
            })

        return meta

    def updateMeta(self, name, json):

        if self.modelsDefinedOnDataset(name) is not None:
            raise Exception("Dataset cannot be deleted. Models are defined on this dataset.")

        for obj in self.meta['data']:
            if obj["name"] == name:
                obj["numericCols"] = json['numericCols']
                obj["enumCols"] = json['enumCols']
                self.repository.update_meta(self.meta)
                return {
                    "name": name,
                    "numericCols": json['numericCols'],
                    "enumCols": json['enumCols']
                }

        raise Exception("Dataset not found")

    def deleteMeta(self, name):

        if self.modelsDefinedOnDataset(name) is not None:
            raise Exception("Dataset cannot be deleted. Models are defined on this dataset.")

        dataset = Utilities.filter(self.meta["data"], "name", name)

        if dataset is not None:
            self.meta['data'].remove(dataset)
            self.repository.update_meta(self.meta)
            return {
                "name": name
            }

        raise Exception("Dataset not found")

    def modelsDefinedOnDataset(self, name):
        return Utilities.filter(self.meta["models"], "data", name)


    ##################
    # get All Models
    ##################

    def getAllModels(self):

        models = []

        for model in self.meta["models"]:
            models.append(model)

        return models

    ##################
    # crud apis
    ##################

    def create(self, json):

        name = json.get('name').strip()
        predictOn = json.get('predictOn')
        featureCols = json.get('featureCols')
        data = json.get('data')

        if not name or not predictOn or not featureCols or not data:
            raise Exception("Invalid Model.")

        data_instance = Utilities.filter(self.meta["data"], "name", data)
        if data_instance is None:
            raise Exception("Dataset not found")

        # append predict-on cols to feature Cols
        if featureCols.count(predictOn) == 0:
            featureCols.append(predictOn)

        enumCols, numericCols = self.parseCols(featureCols, data_instance)

        # get model instance
        model = Model(name, enumCols, numericCols, [], predictOn, data, False, False)

        # check if the model already exist
        if Utilities.filter(self.meta["models"], "name", model.name) is not None:
            # throw exception here
            raise Exception("Model already exists.")
        else:
            self.meta["models"].append(model.to_json())

        self.repository.update_meta(self.meta)

        return model

    def get(self, name):

        # check if model exists
        model_meta = Utilities.filter(self.meta["models"], "name", name)
        if model_meta is not None:
            return model_meta
        else:
            raise Exception("Model not found.")

    def update(self, model):

        self.delete(model.get('name'))

        return self.create(model)

    def delete(self, name):

        # check if model exists
        model_meta = Utilities.filter(self.meta["models"], "name", name)
        if model_meta is not None:
            self.meta["models"].remove(model_meta)
        else:
            raise Exception("Model not found")

        # update meta in s3
        self.repository.update_meta(self.meta)

        # delete if in-mem instance exists
        model_instance = Utilities.filter_name(self.models, name)
        if model_instance is not None:
            self.models.remove(model_instance)

        return model_meta

    ###############################
    # Generate Model
    ###############################

    def generate(self, name):

        # check if model exists
        model_meta = self.get(name)

        # if model is generated throw error
        if model_meta['generated']:
            raise Exception("Model already generated.")

        # get data instance
        data_instance = Utilities.filter(self.meta["data"], "name", model_meta["data"])

        if data_instance is None:
            raise Exception("Data instance not found.")

        # prediction_columns = model_meta["featureCols"]
        # enumCols, numericCols = self.parseCols(prediction_columns, data_instance)

        enumCols = model_meta["enumCols"]
        numericCols = model_meta["numericCols"]
        prediction_columns = enumCols.__add__(numericCols)

        model = Model(name, enumCols, numericCols, [], model_meta["predictOn"], model_meta["data"], False)

        # get file from s3
        file = self.repository.get_file(data_instance["key"])
        auto_data = pd.read_csv(io.BytesIO(file.read()))

        # keep only those cols in dataset which are applicable in this model
        auto_data = auto_data[prediction_columns]

        auto_data = auto_data.replace('?', np.nan)

        # iterate on numeric cols
        for col in numericCols:
            auto_data[col] = pd.to_numeric(auto_data[col], errors='coerce')

        # for classification models
        if enumCols.__contains__(model.predictOn):
            enumCols.remove(model.predictOn)

        # add enum cols
        auto_data = pd.get_dummies(auto_data, columns=enumCols)

        auto_data = auto_data.dropna()

        X = auto_data.drop(model.predictOn, axis=1)

        # Taking the label price
        Y = auto_data[model.predictOn]

        # Splitting into 80% for training set and 20% for testing set to see accuracy
        X_train, x_test, Y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

        if ModelManager.is_classification_model(data_instance, model.predictOn):
            classification_model = tree.DecisionTreeClassifier()
            classification_model.fit(X_train, Y_train)
            DecisionTreeClassifier(class_weight=None, criterion='gini', max_depth=None,
                                   max_features=None, max_leaf_nodes=None, min_impurity_decrease=0.0,
                                   min_impurity_split=None, min_samples_leaf=1, min_samples_split=2,
                                   min_weight_fraction_leaf=0.0, presort=False, random_state=None, splitter='best')
            classification_model.score(X_train, Y_train)
            model.classificationModel = {
                "object": classification_model,
                "score_train": ModelManager.get_score(classification_model.score(X_train, Y_train)),
                "score_test": ModelManager.get_score(classification_model.score(x_test, y_test))
            }

        else:

            # create linear regression model

            linear_model = LinearRegression()
            linear_model.fit(X_train, Y_train)
            LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)
            score_train = linear_model.score(X_train, Y_train)
            score_test = linear_model.score(x_test, y_test)

            predictors = X_train.columns

            coef = pd.Series(linear_model.coef_, predictors).sort_values()

            y_predict = linear_model.predict(x_test)

            model.linearModel = {
                "object": linear_model,
                "actual": pd.Series(y_test.values).values.tolist()[0:100],
                "predicted": pd.Series(y_predict).values.tolist()[0:100],
                "score_train": ModelManager.get_score(score_train),
                "score_test": ModelManager.get_score(score_test),
                "coef": ModelManager.parse_coef(coef)
            }

            # create lasso model
            lasso_model = Lasso(alpha=5, normalize=True)
            lasso_model.fit(X_train, Y_train)

            score_lasso_train = lasso_model.score(X_train, Y_train)
            coef_lasso = pd.Series(lasso_model.coef_, predictors).sort_values()
            y_predict_lasso = lasso_model.predict(x_test)
            score_lasso_test = lasso_model.score(x_test, y_test)

            # model.lassoModel["in-memory-object"] = lasso_model
            model.lassoModel = {
                "object": lasso_model,
                "actual": pd.Series(y_test.values).values.tolist()[0:100],
                "predicted": pd.Series(y_predict_lasso).values.tolist()[0:100],
                "score_train": ModelManager.get_score(score_lasso_train),
                "score_test": ModelManager.get_score(score_lasso_test),
                "coef": ModelManager.parse_coef(coef_lasso)
            }

        model.generated = True
        model.generatedCols = list(x_test.columns.values)
        model.inMemory = True

        # keep the instance in-memory
        self.models.append(model)

        # update instance in s3
        self.update_model_in_s3(model)

        return model

    def hibernate_model(self, name):
        model_meta = self.get(name)

        # validate if the model is generated
        if not model_meta["generated"]:
            raise Exception("model is not generated.")

        if not model_meta["inMemory"]:
            raise Exception("model is already hibernated.")

        model_instance = Utilities.filter_name(self.models, name)

        # remove instance from dictionary
        if model_instance is not None:
            model_instance.inMemory = False
            self.models.remove(model_instance)

        # update the in-memory flag in meta
        model_meta_instance = Utilities.filter(self.meta["models"], "name", name)

        if model_meta_instance is not None:
            model_meta_instance["inMemory"] = False
            self.repository.update_meta(self.meta)

        return model_instance

    def activate_model(self, name):
        model_meta = self.get(name)

        # validate if the model is generated
        if not model_meta["generated"]:
            raise Exception("model is not generated.")

        model_instance = Utilities.filter_name(self.models, name)

        # model instance already in memory
        if model_instance is not None:
            return model_instance

        # create model instance
        name = model_meta.get('name')
        predictOn = model_meta.get('predictOn')
        enumCols = model_meta.get('enumCols')
        numericCols = model_meta.get('numericCols')
        generatedCols = model_meta.get('generatedCols')
        data = model_meta.get('data')

        if not name or not predictOn or not data:
            raise Exception("Invalid Model.")

        data_instance = Utilities.filter(self.meta["data"], "name", data)
        if data_instance is None:
            raise Exception("Dataset not found")

        # get model instance
        model = Model(name, enumCols, numericCols, generatedCols,  predictOn, data, True)
        if ModelManager.is_classification_model(data_instance, model.predictOn):
            model.classificationModel = dict(model_meta.get("classificationModel"))

            # get keys and un serialize model object
            if model.classificationModel["key"] is not None:
                model.classificationModel["object"] = pickle.loads(self.repository.get_file(model.classificationModel["key"]).read())
        else:
            model.linearModel = dict(model_meta.get("linearModel"))
            model.lassoModel = dict(model_meta.get("lassoModel"))

            # get keys and un serialize model object
            if model.linearModel["key"] is not None:
                model.linearModel["object"] = pickle.loads(self.repository.get_file(model.linearModel["key"]).read())

            # get keys and un serialize model object
            if model.lassoModel["key"] is not None:
                model.lassoModel["object"] = pickle.loads(self.repository.get_file(model.lassoModel["key"]).read())

        # update the model instance in the dictionary
        model.inMemory = True
        self.models.append(model)

        # update meta in memory flag
        model_meta = Utilities.filter(self.meta["models"], "name", name)
        if model_meta is not None:
            model_meta["inMemory"] = True
            self.repository.update_meta(self.meta)

        return model

    def predict(self, json):
        model_name = json["model"]
        predict_row = json["predictRow"]
        predict_columns = json["predictColumns"]

        if model_name is None or predict_row is None:
            raise Exception("Invalid params")

        model_instance = Utilities.filter_name(self.models, model_name)

        if model_instance is None:
            raise Exception("Model not found. Activate the model before running prediction.")

        if not model_instance.generated:
            raise Exception("Model is not generated.")

        data = model_instance.data

        data_instance = Utilities.filter(self.meta["data"], "name", data)
        if data_instance is None:
            raise Exception("Dataset not found")

        enumCols, numericCols = self.parseCols(predict_columns, data_instance)

        df = pd.DataFrame(columns=predict_columns)
        df.loc['0'] = predict_row
        df = df.replace('?', np.nan)

        for col in numericCols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = pd.get_dummies(df, enumCols)

        user_input_cols = list(df.columns.values)
        user_input_row = []

        for col in model_instance.generatedCols:
            if user_input_cols.__contains__(col):
                user_input_row.append(df[col].get(0))
            else:
                user_input_row.append(0)

        # should contain all cols in same order
        predict_df = pd.DataFrame(columns=model_instance.generatedCols)
        predict_df.loc['0'] = user_input_row

        if ModelManager.is_classification_model(data_instance, model_instance.predictOn):
            classification_model = model_instance.classificationModel["object"]
            classification_predict = classification_model.predict(predict_df)

            row = {
                "classification_predict": pd.Series(classification_predict).values.tolist(),
            }
        else:
            linear_model = model_instance.linearModel["object"]
            linear_predict = linear_model.predict(predict_df)

            lasso_model = model_instance.lassoModel["object"]
            lasso_predict = lasso_model.predict(predict_df)

            row = {
                "linear_predict": pd.Series(linear_predict).values.tolist(),
                "lasso_predict": pd.Series(lasso_predict).values.tolist()
            }
        return row

    # to be used only for generated models
    # for serializing model instances and storing in s3
    def update_model_in_s3(self, model):

        # delete info from meta
        model_meta_instance = Utilities.filter(self.meta["models"], "name", model.name)

        if model_meta_instance is not None:
            self.meta["models"].remove(model_meta_instance)

        model_meta = {
            "name": model.name,
            "generated": model.generated,
            "inMemory": model.inMemory,
            "enumCols": model.enumCols,
            "numericCols": model.numericCols,
            "generatedCols": model.generatedCols,
            "predictOn": model.predictOn,
            "data": model.data
        }

        data_instance = Utilities.filter(self.meta["data"], "name", model.data)
        if data_instance is None:
            raise Exception("Dataset not found")

        if ModelManager.is_classification_model(data_instance, model.predictOn):
            # serialize classification model
            classification_model_key = self.repository.models_directory + model.name + "_classification"
            self.repository.write_file(classification_model_key, pickle.dumps(model.classificationModel["object"]))

            model_meta["classificationModel"] = {
                "key": classification_model_key,
                "score_train": model.classificationModel["score_train"],
                "score_test": model.classificationModel["score_test"],
            }

        else:
            # serialize linear model
            linear_model_key = self.repository.models_directory + model.name + "_linear"
            self.repository.write_file(linear_model_key, pickle.dumps(model.linearModel["object"]))

            # serialize lasso model
            lasso_model_key = self.repository.models_directory + model.name + "_lasso"
            self.repository.write_file(lasso_model_key, pickle.dumps(model.lassoModel["object"]))

            model_meta["linearModel"] = {
                "key": linear_model_key,
                "actual": model.linearModel["actual"],
                "predicted": model.linearModel["predicted"],
                "score_train": model.linearModel["score_train"],
                "score_test": model.linearModel["score_test"],
                "coef": model.linearModel["coef"]
            }
            model_meta["lassoModel"] = {
                "key": lasso_model_key,
                "actual": model.lassoModel["actual"],
                "predicted": model.lassoModel["predicted"],
                "score_train": model.lassoModel["score_train"],
                "score_test": model.lassoModel["score_test"],
                "coef": model.lassoModel["coef"]
            }

        # update meta
        self.meta["models"].append(model_meta)

        # save meta
        self.repository.update_meta(self.meta)

        return

    def parseCols(self, featureCols, data_instance):

        enumCols = []
        numericCols = []

        for col in featureCols:
            if data_instance["numericCols"].count(col):
                numericCols.append(col)
            if data_instance["enumCols"].count(col):
                enumCols.append(col)

        return enumCols, numericCols

    @staticmethod
    def is_classification_model(data_instance, predictOn):
        if data_instance["enumCols"].count(predictOn) > 0:
            return True
        return False

    @staticmethod
    def get_score(score):
        if score != Model.emptyScore:
            score = str(round(score * 100, 2)) + "%"
        return score

    @staticmethod
    def parse_coef(series):
        positive_coef_key = []
        positive_coef_value = []
        negative_coef_key = []
        negative_coef_value = []

        keys = pd.Series(series).keys().tolist()

        for key in keys:
            value = series.get(key)
            if value > 0:
                positive_coef_key.append(key)
                positive_coef_value.append(value)

            if value < 0:
                negative_coef_key.append(key)
                negative_coef_value.append(value)

        coef = {
            "positive_key": positive_coef_key[::-1][0:5],
            "positive_val": positive_coef_value[::-1][0:5],
            "negative_key": negative_coef_key[0:5],
            "negative_val": negative_coef_value[0:5],
        }

        return coef