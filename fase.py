class Fase:
    def __init__(self, numero, par, tee, buraco_pos,
                 paredes=None, areias=None, aguas=None,
                 tuneis=None, esteiras=None, paredes_moveis=None):
        self.numero = numero
        self.par = par
        self.tee = tee
        self.buraco_pos = buraco_pos
        self.paredes = paredes or []
        self.areias = areias or []
        self.aguas = aguas or []
        self.tuneis = tuneis or []
        self.esteiras = esteiras or []
        self.paredes_moveis = paredes_moveis or []
