class Fase:
    def __init__(self, numero, par, tee, buraco_pos,
                 paredes=None, aguas=None, areias=None, esteiras=None, tuneis=None):
        self.numero = numero
        self.par = par
        self.tee = tee
        self.buraco_pos = buraco_pos
        self.paredes = paredes or []
        self.aguas = aguas or []
        self.areias = areias or []
        self.esteiras = esteiras or []
        self.tuneis = tuneis or []
