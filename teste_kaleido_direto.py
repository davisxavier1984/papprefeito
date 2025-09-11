#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste direto do kaleido para captura de gráficos Plotly
"""

import os
import sys

def testar_kaleido():
    """Testa captura direta com kaleido"""
    print("Testando kaleido diretamente...")
    
    try:
        import plotly.graph_objects as go
        
        # Criar um gráfico simples
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13]))
        fig.update_layout(title="Teste Kaleido")
        
        print("Gráfico criado com sucesso")
        
        # Tentar capturar com diferentes engines
        engines = ['auto', 'kaleido', 'orca']
        
        for engine in engines:
            try:
                print(f"\nTentando com engine: {engine}")
                img_bytes = fig.to_image(format="png", width=400, height=300, engine=engine)
                if img_bytes:
                    print(f"SUCCESS! {engine} funcionou - {len(img_bytes)} bytes")
                    with open(f"teste_kaleido_{engine}.png", "wb") as f:
                        f.write(img_bytes)
                    return True
                else:
                    print(f"FAIL - {engine} retornou vazio")
            except Exception as e:
                print(f"ERRO {engine}: {e}")
        
        return False
        
    except Exception as e:
        print(f"Erro geral: {e}")
        return False

if __name__ == "__main__":
    # Definir variáveis de ambiente que podem ajudar
    os.environ['MPLBACKEND'] = 'Agg'  # Matplotlib backend não-interativo
    os.environ['DISPLAY'] = ':99'  # Virtual display (não vai funcionar no Windows, mas não faz mal)
    
    sucesso = testar_kaleido()
    if sucesso:
        print("\n✅ Kaleido funcionando!")
    else:
        print("\n❌ Kaleido não conseguiu capturar imagens")
    
    sys.exit(0 if sucesso else 1)