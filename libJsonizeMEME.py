import json, sys
class jsonizMeme:
    def __init__(self):
        self.header = ""
        self.meme_dict = dict()
    def stdPrint(self,*args, **kwargs):
        print(*args, **kwargs)
    def errPrint(self,*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)
    def grab(self,target_path):
        meme = open(target_path).read().replace("\n\n\n","\n\n").replace("\t", " ").replace("  ", " ").split("MOTIF ")
        self.header = meme[0]
        if "#header" not in self.meme_dict.keys():
            self.meme_dict["#header"] = self.header
            self.errPrint(F"# Use header info from {target_path}")
        motif_dict = {n.split("\n")[0] : F"MOTIF {n}" for n in meme[1:]}
        duplicate_list = [n for n in motif_dict.keys() if n in self.meme_dict.keys()]
        if len(duplicate_list) > 0:
            self.errPrint("# Duplicated id: {}".format(", ".join(duplicate_list)))
        self.meme_dict.update(motif_dict)
    def exportJSON(self,target_path):
        with open(target_path,"w") as target_handle:
            json.dump(self.meme_dict, target_handle, sort_keys=True, indent=1)
    def exportMEME(self,target_path):
        if self.header != "":
            with open(target_path,"w") as target_handle:
                target_handle.write("".join([self.header]+[self.meme_dict[n] for n in sorted(list(self.meme_dict.keys())) if n[0] != "#"]))
        else:
            self.errPrint("# ERROR: No header. Please at least grab a meme file")
    def exportPrint(self):
        self.stdPrint("".join([self.header]+[self.meme_dict[n] for n in sorted(list(self.meme_dict.keys())) if n[0] != "#"]))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Merge meme files or convert meme file, support MEME format (input and output) and json (output)")
    parser.add_argument("-o", "--meme", type=str, help="output file (meme format)")
    parser.add_argument("-j", "--json", type=str, help="output file (json format)")
    parser.add_argument("file", type=str, nargs="+", help="meme files")
    args = parser.parse_args()

    JSONizMEME = jsonizMeme()
    for target_meme in args.file:
        JSONizMEME.grab(target_meme)
    if not args.meme and not args.json:
        JSONizMEME.errPrint("# Required output path if export as file")
        JSONizMEME.errPrint("# Print out as stdout")
        JSONizMEME.exportPrint()
    if args.json:
        JSONizMEME.exportJSON(args.json)
    if args.meme:
        JSONizMEME.exportMEME(args.meme)
