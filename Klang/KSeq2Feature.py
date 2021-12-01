from . import Kfeature as fc

class SequenceTransformer():
    def __init__(self,calculators:list = None,addcalc = None):
        all_fns = {}
        for fn in dir(fc):
            if callable(getattr(fc,fn)) and 'stypes' in getattr(fc,fn).__dict__ :
                all_fns[getattr(fc,fn).__dict__['name']] = {'func':getattr(fc,fn),'name':getattr(fc,fn).__dict__['name']}


        if calculators is None:
            self.fns = all_fns
        else:
            self.fns = {}
            for c in calculators:

                 if c.get("fname"):
                    name = c.get("fname")
                 else:
                    name = c.get("name")
                       
                 self.fns[name] = all_fns[c.get("name")]
                 if c.get('param'):
                    self.fns[name]['param'] = c.get('param')
                 if c.get('compare'):
                    self.fns[name]['compare'] = c.get('compare')

                 self.fns[name]['name'] = name

        if addcalc is not None:
            for c in addcalc:
                name = c.get('name')
                fname = c.get('fname')
                self.fns[fname] = {
                    'func':all_fns[name].get('func'),
                    'name':fname,
                    'param':c.get('param'),
                    'compare':c.get('compare'),
                }


        # 按类型 整理
        # 0 for boolean, 1 for numericla, 2 for categorical
        self.type_fns = {0:[],1:[],2:[]}

        for fname,func in self.fns.items():
            for i in func.get('func').__dict__['stypes']:
                self.type_fns[i].append(fname)

    def get_feature_names(self):
        """
        get feature names
        :return:
        """
        return list(self.fns.keys()) 



    def transform(self,x , stype=1):
        ftrs = {}
        executing_fns = self.type_fns[stype]
        for fname in executing_fns:
              ftrs[fname + '.' + x.name] = self._transform_fn(fname,x.values)

        return ftrs

    def _transform_fn(self,fname,v):
        f = self.fns[fname]
        try:
            param = f.get('param')
            if param is not None:
                ret = f.get('func')(v,param)
            else:
                ret = f.get('func')(v)

            # 如果设置了做比较参考需要计算比较结果
            if f.get('compare') is not None:
                ret = (ret - v[f.get('compare')]) / v[f.get('compare')] 
            return ret

        except ZeroDivisionError:
            return 0

