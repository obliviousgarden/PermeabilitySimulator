import json
import os
import shutil
import sys
from decimal import Decimal


class ParameterInfo:
    def __init__(self, description: str, name: str, symbol: str, from_value: float, to_value: float,
                 default_value: float, unit: str, is_log: bool):
        self.description = description
        self.name = name
        self.symbol = symbol
        self.from_value = from_value
        self.to_value = to_value
        self.default_value = default_value
        self.unit = unit
        self.is_log = is_log

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return {"description": self.description, "name": self.name, "symbol": self.symbol,
                "from_value": str(self.from_value), "to_value": str(self.to_value),
                "default_value": str(self.default_value),
                "unit": self.unit, "is_log": self.is_log}

    def to_str(self):
        return f"{self.name} ({self.symbol}) : {self.description}" \
               f"\n= {self.default_value} ({self.from_value} ~ {self.to_value})" \
               f" [Unit] = [{self.unit}] " \
               f"\nLOG? : {self.is_log} "


class ParameterInfoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ParameterInfo):
            # Convert ParameterInfo object to a serializable dictionary
            return {"description": obj.description, "name": obj.name, "symbol": obj.symbol,
                    "from_value": str(obj.from_value), "to_value": str(obj.to_value),
                    "default_value": str(obj.default_value),
                    "unit": obj.unit, "is_log": obj.is_log}
        return super().default(obj)


class ParameterInfoDict:
    parameter_info_dict = {}
    __base_path = ''
    __user_data_dir = ''
    __json_file_path = ''

    def __init__(self, user_data_dir):
        self.__user_data_dir = user_data_dir
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            self.__base_path = sys._MEIPASS
        else:
            # Running as script
            self.__base_path = os.path.dirname(__file__)
        if self.parameter_info_dict == {}:
            # list 是空的话，那么需要从json文件初始化json
            self.__json_file_path = os.path.join(user_data_dir, "parameter_info.json")
            if os.path.exists(self.__json_file_path) is False:
                # 如果不存在，那么把__base_path路径下的文件复制到响应路径
                shutil.copy(os.path.join(self.__base_path, 'parameter_info.json'), self.__user_data_dir)
            with open(self.__json_file_path, 'r', encoding="utf-8") as json_file:
                data_dict = json.load(json_file)
                for param_name, param_dict in data_dict.items():
                    self.parameter_info_dict[param_name] = ParameterInfo.from_dict(param_dict)
            # print('ParameterInfoInit:', json.dumps(self.parameter_info_dict, cls=ParameterInfoEncoder, indent=4))

    def update_json(self):
        with open(self.__json_file_path, 'w') as json_file:
            json_data = json.dumps(self.parameter_info_dict, cls=ParameterInfoEncoder, indent=4)
            print(json_data)
            json_file.write(json_data)

    def add_update_by_info(self, new_parameter_info: ParameterInfo) -> bool:
        ParameterInfoDict.parameter_info_dict[new_parameter_info.name] = new_parameter_info
        self.update_json()
        return True

    # FIXME:封印删除方法,因为删除参数会导致严重的问题使得物理模型不可用
    def del_by_name(self, del_parameter_name: str) -> bool:
        if del_parameter_name in ParameterInfoDict.parameter_info_dict.keys():
            print(f'Delete Parameter:{del_parameter_name}')
        else:
            return False


if __name__ == "__main__":
    prefix = ParameterInfoDict("D:\\PycharmProjects\\DielectricRelaxationSimulator")
