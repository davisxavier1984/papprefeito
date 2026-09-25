/**
 * Relatórios em lote (stories 3.4 e 3.5)
 * Seleciona vários municípios e gera os relatórios PAP Prefeito e/ou Detalhado num único ZIP.
 * Para cada município, o backend usa os valores revisados na tela Início; se não houver para a
 * competência, calcula automaticamente (regras da story 3.3) e salva.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Alert, App, Button, Card, Checkbox, Progress, Space, Typography } from 'antd';
import { CheckCircleOutlined, DownloadOutlined } from '@ant-design/icons';
import { apiClient } from '../services/api';
import SeletorVariosMunicipios from '../components/Selectors/SeletorVariosMunicipios';
import { competenciaValida, guardarLoteAtivo, lerLoteAtivo, ordenarMunicipios, statusMaisRecente } from '../utils/municipiosLote';
import type { LoteStatus, MunicipioLote, TipoRelatorio } from '../types';

const { Title, Text } = Typography;

const baixarArquivo = (blob: Blob, nome: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', nome);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

const RelatoriosLote: React.FC = () => {
  const { message } = App.useApp();

  // Seleção acumulada entre UFs, indexada pelo código IBGE
  const [selecionados, setSelecionados] = useState<Record<string, MunicipioLote>>({});
  const [competencia, setCompetencia] = useState('');
  const [tipos, setTipos] = useState<TipoRelatorio[]>(['prefeito']);
  const [lote, setLote] = useState<LoteStatus | null>(null);
  const [iniciando, setIniciando] = useState(false);
  const baixadoRef = useRef<string | null>(null);

  const listaSelecionados = useMemo(() => ordenarMunicipios(selecionados), [selecionados]);

  const gerar = async () => {
    if (iniciando) return;
    setIniciando(true);
    try {
      baixadoRef.current = null;
      const novo = await apiClient.criarLote({ competencia, tipos, municipios: listaSelecionados, sem_perdas: 'regras' });
      guardarLoteAtivo(novo.id);
      setLote(novo);
    } catch {
      message.error('Não foi possível iniciar a geração dos relatórios.');
    } finally {
      setIniciando(false);
    }
  };

  // Retoma o acompanhamento de um lote iniciado antes de sair da página
  useEffect(() => {
    const id = lerLoteAtivo();
    if (!id) return;
    apiClient
      .statusLote(id)
      .then((status) => setLote((atual) => atual ?? status))
      .catch(() => guardarLoteAtivo(null));
  }, []);

  // Acompanha o andamento. Uma chamada por vez; respostas fora de ordem são ignoradas
  // e só desiste depois de 3 falhas seguidas.
  const loteId = lote?.id;
  const loteStatus = lote?.status;
  useEffect(() => {
    if (!loteId || loteStatus !== 'processando') return;
    let cancelado = false;
    let falhas = 0;
    let timer: number | undefined;
    const acompanhar = async () => {
      try {
        const novo = await apiClient.statusLote(loteId);
        falhas = 0;
        if (!cancelado) setLote((atual) => statusMaisRecente(atual, novo));
      } catch {
        falhas += 1;
        if (falhas >= 3) {
          if (!cancelado) {
            message.error('Perdi o acompanhamento da geração. Gere novamente.');
            guardarLoteAtivo(null);
            setLote(null);
          }
          return;
        }
      }
      if (!cancelado) timer = window.setTimeout(acompanhar, 2000);
    };
    timer = window.setTimeout(acompanhar, 2000);
    return () => {
      cancelado = true;
      window.clearTimeout(timer);
    };
  }, [loteId, loteStatus, message]);

  // Lote terminou (com sucesso ou erro): para de tentar retomar ao voltar à página;
  // só baixa o ZIP quando concluído.
  useEffect(() => {
    if (!lote) return;
    if (lote.status === 'erro') {
      guardarLoteAtivo(null);
      return;
    }
    if (lote.status !== 'concluido' || baixadoRef.current === lote.id) return;
    baixadoRef.current = lote.id;
    guardarLoteAtivo(null);
    if (lote.arquivos === 0) {
      message.warning('Nenhum relatório foi gerado. Veja o motivo abaixo.');
      return;
    }
    apiClient
      .baixarLote(lote.id)
      .then((blob) => {
        baixarArquivo(blob, `relatorios_${lote.competencia}.zip`);
        message.success(`${lote.arquivos} relatório(s) gerado(s).`);
      })
      .catch(() => message.error('Os relatórios foram gerados, mas o download falhou. Tente baixar de novo.'));
  }, [lote, message]);

  const baixarNovamente = () => {
    if (!lote) return;
    apiClient
      .baixarLote(lote.id)
      .then((blob) => baixarArquivo(blob, `relatorios_${lote.competencia}.zip`))
      .catch(() => message.error('Não foi possível baixar o arquivo.'));
  };

  const gerando = lote?.status === 'processando';
  const podeGerar = listaSelecionados.length > 0 && competenciaValida(competencia) && tipos.length > 0 && !gerando;

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={3} style={{ marginBottom: 4 }}>Relatórios em lote</Title>
        <Text type="secondary">
          Selecione os municípios e o tipo de relatório. Os valores usados são os revisados na tela Início; quando o
          município ainda não tiver valores na competência, eles são calculados automaticamente e ficam disponíveis
          para revisão na tela Início.
        </Text>
      </div>

      <Card title="1. Municípios e competência">
        <SeletorVariosMunicipios
          selecionados={selecionados}
          onChange={setSelecionados}
          competencia={competencia}
          onCompetenciaChange={setCompetencia}
        />
      </Card>

      <Card title="2. Tipo de relatório">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Checkbox.Group
            value={tipos}
            onChange={(v) => setTipos(v as TipoRelatorio[])}
            options={[
              { label: 'Relatório PAP Prefeito', value: 'prefeito' },
              { label: 'Relatório Detalhado', value: 'detalhado' },
            ]}
          />
          <Space wrap>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={gerar}
              loading={iniciando || gerando}
              disabled={!podeGerar || iniciando}
            >
              Gerar {listaSelecionados.length * tipos.length} relatório(s)
            </Button>
            {!tipos.length && <Text type="danger">Escolha ao menos um tipo de relatório.</Text>}
          </Space>

          {lote && (
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Progress
                percent={lote.total ? Math.round((lote.processados / lote.total) * 100) : 0}
                status={lote.status === 'erro' ? 'exception' : lote.status === 'concluido' ? 'success' : 'active'}
              />
              <Text>
                {lote.processados} de {lote.total} municípios · {lote.arquivos} relatório(s) gerado(s)
                {lote.calculados > 0 && ` · ${lote.calculados} com valores calculados agora (revise na tela Início, se quiser)`}
              </Text>
              {lote.status === 'concluido' && lote.arquivos > 0 && (
                <Button icon={<CheckCircleOutlined />} onClick={baixarNovamente}>
                  Baixar o ZIP novamente
                </Button>
              )}
              {lote.erros.length > 0 && (
                <Alert
                  type="error"
                  showIcon
                  message="Não foi possível gerar para alguns municípios"
                  description={
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {lote.erros.map((e) => <li key={e}>{e}</li>)}
                    </ul>
                  }
                />
              )}
            </Space>
          )}
        </Space>
      </Card>
    </Space>
  );
};

export default RelatoriosLote;
