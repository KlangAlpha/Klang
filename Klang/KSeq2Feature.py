import .Kfeature as fc

class SequenceTransformer():
    def __init__(self,calculators:list = None):
        all_fns = {}
        for fn in dir(fc):
            if callable(getattr(fc,fn)) and 'name' in getattr(fc,fn).__dict__:
                all_fns[getattr(fc,fn).__dict__['name']] = getattr(fc,fn)


        if calculators is None:
            self.fns = all_fns
        else:
            self.fns = {}
            for c in calculators:
                if c in all_fns:
                    self.fns[c] = all_fns[c]



        # 按类型 整理
        # 0 for boolean, 1 for numericla, 2 for categorical
        self.type_fns = {0:[],1:[],2:[]}

        for fname,func in self.fns.items():
            for i in func.__dict__['stypes']:
                self.type_fns[i].append(fname)

    def get_feature_names(self):
        """
        get feature names
        :return:
        """
        return list(self.fns.keys()) #list(self.valid_fnames)



    def transform(self,x , stype=1):
        ftrs = {}
        executing_fns = self.type_fns[stype]
        for fname in executing_fns:
              ftrs[fname] = (self._transform_fn(fname,x.values))

        print(ftrs)

    def _transform_fn(self,fname,v):
        f = self.fns[fname]
        try:
            return f(v)
        except ZeroDivisionError:
            return 0


