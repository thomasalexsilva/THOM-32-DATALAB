import math, csv, datetime, argparse
from timeseries_rnn import *

def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--rank_models',                default=False)
    parser.add_argument('--treina',                     default=True)
    parser.add_argument('--grandezas',                  default="ApDX_ApDY")
    parser.add_argument('--efunc',                      default="mse")
    parser.add_argument('--linha',                      default=0)
    parser.add_argument('--linha_max',                  default=None)
    parser.add_argument('--arquivo',                    default='clima_bsb.csv')
    # 1 ano (dados horários) => Último [2014, 2020] na base clima_bsb => [2020] p/ teste
    parser.add_argument('--iteracoes_teste',            default=365*24)
    parser.add_argument('--batch_sizes',                default=None)
    return parser

def main(args):

    if(args.rank_models == "True"):
        print("Gerando ranking de modelos!")
        grupos = MZDN_HF.rank_models("modelos")
        for grupo in grupos:
            for el in grupo:
                print(el)
        return

    X = []
    with open(args.arquivo) as _csv:
        _r = csv.reader(_csv, delimiter=',')
        linha           = args.linha
        linha_max       = args.linha_max

        for row in _r:
            if linha > 0:
                horario = int(float(row[1]))
                data = datetime.datetime.strptime(row[0].split(" ")[0], "%Y-%m-%d")
                # considera rad apenas entre 8 e 16     (nossas estações causam deformidade às 6~7 e 17~18h)
                _rad = row[6] if horario >= 8 and horario <= 16 else 0
                vazio = math.isnan(float(row[3])) or float(row[3]) is None
                if(vazio):
                    continue
                X.append({
                    "data":     data,         
                    "horario":  horario, 
                    "dia_ano":  int(row[2]),     
                    "ano":      int(data.year),      
                    "temp":     float(row[3]),             
                    "hum" :     float(row[4]),             
                    "pres":     float(row[5]),             
                    "rad" :     float(_rad),   
                    "pluv":     float(row[7]),    
                    "choveu":   int(row[8]),
                    "vel":      float(row[9]),
                    "dir":      float(row[10]),
                    "temp_d":   float(row[11]),       
                    "hum_d":    float(row[12]),       
                    "pres_d":   float(row[13]),         
                })
            if(linha_max is not None and linha > linha_max):
                break
            linha += 1

    grandezas_list  = {
        "ApDX_ApDY" : [
                ["temp", "hum", "pres_d", "rad", "pluv"],    
                ["temp", "hum", "pres_d", "rad", "pluv"]     
            ],
        "AX_AY" : [
                ["temp", "hum", "pres", "rad", "pluv"],      
                ["temp", "hum", "pres", "rad", "pluv"]       
            ],
    }
    
    # Filtra apenas as grandezas desejadas
    grandezas = grandezas_list[args.grandezas]
    
    
    # Com referência ao paper anterior, poram subtraídas as grandezas Pres e Chuva (categ). Pres pois foi substituída pelo
    # seu delta horário a fim de resolver incongruências de nível e Chuva (Categ) pois não se pode ter valores discretos na
    # saída com uma rede com função de erro MSE/MAE. Precisa-se de uma rede dedicada para esta grandeza.
    
    hps = [
        #----------------------------------------------------------------------------------
        #---------------------------------- bidirecional ----------------------------------
        # -----  batch size 32
        # 10 layers
        MZDN_HP(grandezas, args.efunc, 10,  48, ARQ_ENC_DEC_BID, 0),
        MZDN_HP(grandezas, args.efunc, 10,  24, ARQ_ENC_DEC_BID, 0),
        # 50 layers
        MZDN_HP(grandezas, args.efunc, 50,  48, ARQ_ENC_DEC_BID, 0),
        MZDN_HP(grandezas, args.efunc, 50,  24, ARQ_ENC_DEC_BID, 0),
        # 100 layers
        MZDN_HP(grandezas, args.efunc, 100, 48, ARQ_ENC_DEC_BID, 0),
        MZDN_HP(grandezas, args.efunc, 100, 24, ARQ_ENC_DEC_BID, 0),
        # 10 layers
        MZDN_HP(grandezas, args.efunc, 10,  48, ARQ_ENC_DEC_BID, 0.25),
        MZDN_HP(grandezas, args.efunc, 10,  24, ARQ_ENC_DEC_BID, 0.25),
        # 50 layers
        MZDN_HP(grandezas, args.efunc, 50,  48, ARQ_ENC_DEC_BID, 0.25),
        MZDN_HP(grandezas, args.efunc, 50,  24, ARQ_ENC_DEC_BID, 0.25),
        # 100 layers
        MZDN_HP(grandezas, args.efunc, 100, 48, ARQ_ENC_DEC_BID, 0.25),
        MZDN_HP(grandezas, args.efunc, 100, 24, ARQ_ENC_DEC_BID, 0.25),
        # 10 layers
        MZDN_HP(grandezas, args.efunc, 10,  48, ARQ_ENC_DEC_BID, 0.5),
        MZDN_HP(grandezas, args.efunc, 10,  24, ARQ_ENC_DEC_BID, 0.5),
        # 50 layers
        MZDN_HP(grandezas, args.efunc, 50,  48, ARQ_ENC_DEC_BID, 0.5),
        MZDN_HP(grandezas, args.efunc, 50,  24, ARQ_ENC_DEC_BID, 0.5),
        # 100 layers
        MZDN_HP(grandezas, args.efunc, 100, 48, ARQ_ENC_DEC_BID, 0.5),
        MZDN_HP(grandezas, args.efunc, 100, 24, ARQ_ENC_DEC_BID, 0.5),

        
        #-----------------------------------------------------------------------------------
        #---------------------------------- unidirecional ----------------------------------
        # -----  batch size 32
        # 10 layers
        MZDN_HP(grandezas, args.efunc, 10,  48, ARQ_ENC_DEC, 0),
        MZDN_HP(grandezas, args.efunc, 10,  24, ARQ_ENC_DEC, 0),
        # 50 layers
        MZDN_HP(grandezas, args.efunc, 50,  48, ARQ_ENC_DEC, 0),
        MZDN_HP(grandezas, args.efunc, 50,  24, ARQ_ENC_DEC, 0),
        # 100 layers
        MZDN_HP(grandezas, args.efunc, 100, 48, ARQ_ENC_DEC, 0),
        MZDN_HP(grandezas, args.efunc, 100, 24, ARQ_ENC_DEC, 0),
        # 10 layers
        MZDN_HP(grandezas, args.efunc, 10,  48, ARQ_ENC_DEC, 0.25),
        MZDN_HP(grandezas, args.efunc, 10,  24, ARQ_ENC_DEC, 0.25),
        # 50 layers
        MZDN_HP(grandezas, args.efunc, 50,  48, ARQ_ENC_DEC, 0.25),
        MZDN_HP(grandezas, args.efunc, 50,  24, ARQ_ENC_DEC, 0.25),
        # 100 layers
        MZDN_HP(grandezas, args.efunc, 100, 48, ARQ_ENC_DEC, 0.25),
        MZDN_HP(grandezas, args.efunc, 100, 24, ARQ_ENC_DEC, 0.25),
        # 10 layers
        MZDN_HP(grandezas, args.efunc, 10,  48, ARQ_ENC_DEC, 0.5),
        MZDN_HP(grandezas, args.efunc, 10,  24, ARQ_ENC_DEC, 0.5),
        # 50 layers
        MZDN_HP(grandezas, args.efunc, 50,  48, ARQ_ENC_DEC, 0.5),
        MZDN_HP(grandezas, args.efunc, 50,  24, ARQ_ENC_DEC, 0.5),
        # 100 layers
        MZDN_HP(grandezas, args.efunc, 100, 48, ARQ_ENC_DEC, 0.5),
        MZDN_HP(grandezas, args.efunc, 100, 24, ARQ_ENC_DEC, 0.5),

    ]

    if(args.treina):
        for i in range(len(hps)):
            hp          = hps[i]
            diretorio   = f"modelos/{args.grandezas}/{args.efunc.upper()}_{hp.arq}_BAT{hp.batch_size}_DOUT{hp.dropout}_HL{hp.h_layers}_BCKW{hp.steps_b}"
            mzdn        = MZDN_HF(diretorio, hp, True)
            mzdn.treinar(X, args.iteracoes_teste)
    else:
        mzdn = MZDN_HF(args.diretorio)
        mzdn.prever(X, 0)



if __name__ == "__main__":
    parser = parse_args()
    args = parser.parse_args()
    main(args)