import argparse
import json
import os
import warnings
import datetime

class GatherOptions():
    def __init__(self):
        parser = argparse.ArgumentParser(description="Scoring thinking game")
               
        current_time = datetime.datetime.now()
        parser.add_argument("--save_dir", default=("Thinking\log\{:%Y%m%d_%H_%M}".format(current_time)), help="path for saving")
        parser.add_argument("--game", default=("oneimagetest"), help="Choose thinking game")

        parser.add_argument("--k_sim", default=10, help="Select topk similar word from fasttext model")
        parser.add_argument("--_layer_depth", default=7, help="Set Ehow tree depth. (the lower number, easier)")
                
        self.parser = parser

    def parse(self, argv=None):
        if argv == None:
            opt = self.parser.parse_args(argv) # for running in jupyter notebook    
        else:
            opt = self.parser.parse_args()
        self.opt = opt
        self.config_path = os.path.join(opt.save_dir, 'opt.json')
    
        os.makedirs(opt.save_dir, exist_ok=True)

        with open(self.config_path, 'w') as f:
            json.dump(self.opt.__dict__, f)
        
        return opt
