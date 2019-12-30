from mag.Mag import Mag_Api
from decorators import timing
mag = Mag_Api()
p = mag.get_paper(2157025439)
r = mag.get_refs(p)
c = mag.get_cits(p)
lp = r + c


@timing
def time_this():
    return mag.get_cits(lp)


time_this()
