
class db:
    fail = False
    def __init__(self,file,sep=','):
        self.sep = sep
        try:
            self.f = open(file,'r')
        except:
            self.fail = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            l = self.f.readline()
            if not l:
                raise StopIteration
            la = l.split('#')
            lb = la[0].strip()
            if lb: break
        return [x.strip() for x in lb.split(self.sep)]

    def close(self):
        self.f.close()
