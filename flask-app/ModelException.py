from flask import jsonify


class ModelException:

    @staticmethod
    def to_json(ex):

        message = "Exception occurred"

        if ex.args:
            message = ex.args[0]

        return jsonify({"error": message})
