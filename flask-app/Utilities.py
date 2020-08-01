
class Utilities:

    @staticmethod
    def filter(arr, key, value):
        for obj in arr:
            if obj[key] == value:
                return obj
        return None

    @staticmethod
    def filter_name(arr, value):
        for obj in arr:
            if obj.name == value:
                return obj
        return None
