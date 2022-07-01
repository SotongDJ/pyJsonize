import os, sys, math
class jsonizeTSV:
    def __init__(self):
        self.input_path = str()
        self.header_list = list()
        self.content_list = list()
        self.id_str = str()
        self.id_dict = dict()
        self.count_bool = False
        self.output_dict = dict()
        self.mute = False
    def print(self,*args, **kwargs):
        if not self.mute:
            print(*args, **kwargs)
    # convert_size(), from: https://gist.github.com/SotongDJ/1296bbeedc5f49573c014a8e65dd707f
    def convert_size(self,size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "{} {}".format(s, size_name[i])
    def deduplicate(self,input_list,output_dict_bool=False):
        duplicate_list = list()
        self.content_list = list()
        for n in input_list:
            if n in duplicate_list:
                self.content_list.append(n)
            else:
                duplicate_list.append(n)
        output_dict = {
            "Unique": self.content_list,
            "Duplicate": duplicate_list,
        }
        if output_dict_bool:
            return output_dict
        else:
            return self.content_list
    def read(self):
        self.print(F"[LOAD] file: \"{self.input_path}\"")
        input_size_int = os.path.getsize(self.input_path)
        self.print("- Filesize: \"{}\"".format(self.convert_size(input_size_int)))
        file_lines = [n for n in open(self.input_path).read().splitlines() if n != ""]
        lines_without_hash = [n for n in file_lines if n[0] != "#"]
        lines_with_tab = [n for n in lines_without_hash if "\t" in n]
        return_bool = True
        if len(lines_with_tab) == 0:
            self.print("[ERROR] Content must more than 0 line")
            return_bool = False
        else:
            if self.header_list == list():
                if len(lines_with_tab) <= 1:
                    self.print("[ERROR] Content with header must more than 1 line")
                    return_bool = False
                else:
                    header_line, *content_lines = lines_with_tab
                    self.header_list.extend(header_line.split("\t"))
                    self.content_list.extend([n.split("\t") for n in content_lines])
            else:
                self.print("[NOTE] use user-provided header list")
                self.content_list.extend([n.split("\t") for n in lines_with_tab])
        if return_bool:
            if len(self.header_list) != len(set(self.header_list)):
                self.print("[WARN] Duplicated column name in header list")
                self.print(self.deduplicate(self.header_list))
            column_count_set = set([len(n) for n in self.content_list])
            if len(column_count_set) != 1:
                self.print("[WARN] Cell count per line no consistent")
                self.print("- Cell count per line:",column_count_set)
        return return_bool
    def determind(self):
        self.print("[ANALYSIS] check column and row")
        determind_index_dict = {i:len(set([n[i] for n in self.content_list])) for i in range(len(self.header_list))}
        determind_dict = {self.header_list[x]:x for x,y in determind_index_dict.items() if y == len(self.content_list)}
        determind_list = sorted(list(determind_dict.keys()), key=lambda x : determind_dict[x])
        self.print("- Unique column header: {}".format(determind_list))
        if self.id_str == str():
            if len(determind_list) > 0:
                determind_str = determind_list[0]
                determind_int = determind_dict[determind_str]
                self.print(F"- Selected ID: {determind_str}")
            else:
                self.count_bool = True
                self.print(F"- Selected ID: line count")
        else:
            if self.id_str in self.header_list:
                if self.id_str not in determind_list:
                    self.print(F"[WARN] some values under {self.id_str} column are duplicated, use line count instead")
                    self.count_bool = True
                    self.print(F"- Selected ID: line count")
                determind_int = determind_dict[self.id_str]
                self.print(F"- Selected ID: {self.id_str}")
            else:
                self.print(F"[WARN] {self.id_str} not found, use line count instead")
                self.count_bool = True
                self.print(F"- Selected ID: line count")
        if self.count_bool:
            self.id_dict.update({i:i for i in range(len(self.content_list))})
        else:
            self.id_dict.update({i:self.content_list[i][determind_int] for i in range(len(self.content_list))})
        self.print("[ANALYSIS] finish")
    def conversion(self):
        self.print("[CONVERSION] start")
        self.output_dict.update({id_str:{self.header_list[j]:k for j,k in enumerate(self.content_list[i])} for i,id_str in self.id_dict.items()})
        self.print("[CONVERSION] finish")
        output_size_int = sys.getsizeof(self.output_dict)
        self.print("- Filesize: \"{}\"".format(self.convert_size(output_size_int)))
    def extractAttribute(self,attribute_str):
        self.print("[Extract Attribute] start")
        temp_dict = dict()
        for key_str, value_dict in self.output_dict.items():
            temp_value_dict = dict()
            temp_value_dict.update(value_dict)
            attribute_line_str = value_dict[attribute_str]
            attribute_list = [n.split("=") for n in attribute_line_str.split(";")]
            attribute_dict = {n[0]:n[1] for n in attribute_list if len(n) == 2}
            temp_value_dict.update(attribute_dict)
            temp_dict[key_str] = temp_value_dict
        self.output_dict.update(temp_dict)
        self.print("[Extract Attribute] finish")
        output_size_int = sys.getsizeof(self.output_dict)
        self.print("- Filesize: \"{}\"".format(self.convert_size(output_size_int)))

if __name__ == "__main__":
    import json, argparse
    parser = argparse.ArgumentParser(description="convert tsv with header into json")
    parser.add_argument("tsv", help="tsv file", type=str)
    parser.add_argument("-i","--id", help="select ID column", type=str)
    parser.add_argument("-t","--header", help="header (seperate with comma)", type=str, default="")
    parser.add_argument("-a","--attribute", help="convert attribute into dict", type=str)
    parser.add_argument("-o","--output", help="output json", type=str)
    args = parser.parse_args()

    JsonizeTSV = jsonizeTSV()
    JsonizeTSV.input_path = args.tsv
    if args.header and "," in args.header:
        JsonizeTSV.header_list = args.header.split(",")
    if args.id:
        JsonizeTSV.id_str = args.id
    if JsonizeTSV.read():
        JsonizeTSV.determind()
        JsonizeTSV.conversion()
        if args.attribute in JsonizeTSV.header_list and JsonizeTSV.output_dict != dict():
            JsonizeTSV.extractAttribute(args.attribute)
        elif args.attribute:
            JsonizeTSV.print("ERROR: args.attribute [",args.attribute,"]")
            JsonizeTSV.print("ERROR: JsonizeTSV.output_dict [length: ",len(JsonizeTSV.output_dict),"]")
        if args.output:
            output_str = args.output
        else:
            output_str = ".".join(args.tsv.split(".")[:-1])+"-convert.json"
        if JsonizeTSV.output_dict != dict():
            JsonizeTSV.print(F"\"{args.tsv}\" --> \"{output_str}\"")
            with open(output_str,'w') as output_handle:
                json.dump(JsonizeTSV.output_dict,output_handle,indent=1)
        else:
            JsonizeTSV.print("ERROR: output_dict is empty, EXIT")
    else:
        JsonizeTSV.print("ERROR: Can't read(), EXIT")
