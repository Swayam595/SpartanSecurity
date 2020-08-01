
class Model:

    emptyScore = "--"

    def __init__(self, name='', enumCols=[], numericCols=[], generatedCols=[], predictOn='', data='',generated=False, inMemory=False):

        self.name = name
        self.generated = generated
        self.inMemory = inMemory
        self.enumCols = enumCols
        self.numericCols = numericCols
        self.predictOn = predictOn
        self.data = data
        self.generatedCols = generatedCols
        self.linearModel = {
            "object": None,
            "actual": [],
            "predicted": [],
            "score_train": Model.emptyScore,
            "score_test": Model.emptyScore,
            "coef": []
        }
        self.lassoModel = {
            "object": None,
            "actual": [],
            "predicted": [],
            "score_train": Model.emptyScore,
            "score_test": Model.emptyScore,
            "coef": []
        }
        self.classificationModel = {
            "object": None,
            "score_train": Model.emptyScore,
            "score_test": Model .emptyScore,
        }
        # self.actual = []
        # self.predicted = []
        return

    def to_json(self):
        lassoScoreTrain = self.lassoModel.get("score_train")
        lassoScoreTest = self.lassoModel.get("score_test")
        linearScoreTrain = self.linearModel.get("score_train")
        linearScoreTest = self.linearModel.get("score_test")

        json = {
            "name": self.name,
            "data": self.data,
            "generated": self.generated,
            "inMemory": self.inMemory,
            "predictOn": self.predictOn,
            "enumCols": self.enumCols,
            "generatedCols": self.generatedCols,
            "numericCols": self.numericCols,
            "linearModel": {
                "scoreTrain": linearScoreTrain,
                "scoreTest": linearScoreTest,
                "coef": self.linearModel.get("coef"),
                "actual": self.linearModel.get("actual"),
                "predicted": self.linearModel.get("predicted")
            },
            "lassoModel": {
                "scoreTrain": lassoScoreTrain,
                "scoreTest": lassoScoreTest,
                "coef": self.lassoModel.get("coef"),
                "actual": self.lassoModel.get("actual"),
                "predicted": self.lassoModel.get("predicted")
            }
        }

        return json
