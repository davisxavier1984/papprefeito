/**
 * Relatórios em lote (stories 3.4 e 3.5)
 * Seleciona vários municípios, confere as perdas salvas e gera os relatórios
 * PAP Prefeito e/ou Detalhado num único ZIP.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Alert,
  App,
  Button,
  Card,
  Checkbox,
  Progress,
  Radio,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { CheckCircleOutlined, DownloadOutlined, FileSearchOutlined } from '@ant-design/icons';
import { apiClient } from '../services/api';
import SeletorVariosMunicipios from '../components/Selectors/SeletorVariosMunicipios';
import { competenciaValida, ordenarMunicipios } from '../utils/municipiosLote';
import type { LoteConferenciaItem, LoteStatus, MunicipioLote, TipoRelatorio } from '../types';

const { Title, Text } = Typography;

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

const ORIGEM_LABEL: Record<string, string> = {
  manual: 'manual',
  regra: 'regra',
  estimativa: 'estimativa',
};

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
  const [semPerdas, setSemPerdas] = useState<'ignorar' | 'zero'>('ignorar');

  const [conferencia, setConferencia] = useState<LoteConferenciaItem[] | null>(null);
  const [conferindo, setConferindo] = useState(false);
  const [lote, setLote] = useState<LoteStatus | null>(null);
  const baixadoRef = useRef<string | null>(null);

  const listaSelecionados = useMemo(() => ordenarMunicipios(selecionados), [selecionados]);

  // Qualquer mudança na seleção invalida a conferência anterior
  useEffect(() => {
    setConferencia(null);
  }, [selecionados, competencia]);

  const conferir = async () => {
    try {
      setConferindo(true);
      setConferencia(await apiClient.conferirLote(competencia, listaSelecionados));
    } catch {
      message.error('Não foi possível conferir os municípios. Tente novamente.');
    } finally {
      setConferindo(false);
    }
  };

  const gerar = async () => {
    try {
      baixadoRef.current = null;
      setLote(
        await apiClient.criarLote({ competencia, tipos, municipios: listaSelecionados, sem_perdas: semPerdas })
      );
    } catch {
      message.error('Não foi possível iniciar a geração dos relatórios.');
    }
  };

  // Acompanha o andamento e baixa o ZIP ao terminar
  useEffect(() => {
    if (!lote || lote.status !== 'processando') return;
    const timer = window.setInterval(async () => {
      try {
        setLote(await apiClient.statusLote(lote.id));
      } catch {
        message.error('Perdi o acompanhamento do lote. Gere novamente.');
        setLote(null);
      }
    }, 2000);
    return () => window.clearInterval(timer);
  }, [lote, message]);

  useEffect(() => {
    if (!lote || lote.status !== 'concluido' || baixadoRef.current === lote.id) return;
    baixadoRef.current = lote.id;
    if (lote.arquivos === 0) {
      message.warning('Nenhum relatório foi gerado. Veja os avisos abaixo.');
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
  const podeConferir = listaSelecionados.length > 0 && competenciaValida(competencia) && !gerando;
  const semPerdasCount = conferencia?.filter((c) => !c.tem_perdas).length ?? 0;
  const aGerar = conferencia
    ? semPerdas === 'ignorar'
      ? conferencia.length - semPerdasCount
      : conferencia.length
    : 0;

  const colunas: ColumnsType<LoteConferenciaItem> = [
    { title: 'Município', dataIndex: 'nome', key: 'nome' },
    { title: 'UF', dataIndex: 'uf', key: 'uf', width: 70 },
    {
      title: 'Perdas salvas',
      key: 'tem_perdas',
      width: 150,
      render: (_, r) =>
        r.tem_perdas ? (
          <Tag color="green">Sim</Tag>
        ) : (
          <Tag color={semPerdas === 'ignorar' ? 'default' : 'orange'}>
            {semPerdas === 'ignorar' ? 'Não (fica de fora)' : 'Não (perda zero)'}
          </Tag>
        ),
    },
    {
      title: 'Perda mensal',
      key: 'total',
      align: 'right',
      width: 160,
      render: (_, r) => (r.tem_perdas ? moeda.format(r.total_perda_mensal) : '—'),
    },
    {
      title: 'Origem dos valores',
      key: 'origens',
      render: (_, r) =>
        Object.keys(r.origens).length
          ? Object.entries(r.origens).map(([o, n]) => <Tag key={o}>{`${ORIGEM_LABEL[o] ?? o}: ${n}`}</Tag>)
          : r.tem_perdas
            ? <Text type="secondary">não informada</Text>
            : null,
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={3} style={{ marginBottom: 4 }}>Relatórios em lote</Title>
        <Text type="secondary">
          Selecione vários municípios, confira as perdas salvas e gere os relatórios de uma vez, num arquivo ZIP.
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
        <Space direction="vertical">
          <Checkbox.Group
            value={tipos}
            onChange={(v) => setTipos(v as TipoRelatorio[])}
            options={[
              { label: 'Relatório PAP Prefeito', value: 'prefeito' },
              { label: 'Relatório Detalhado', value: 'detalhado' },
            ]}
          />
          <Radio.Group value={semPerdas} onChange={(e) => setSemPerdas(e.target.value)}>
            <Space direction="vertical">
              <Radio value="ignorar">Municípios sem perdas salvas ficam de fora</Radio>
              <Radio value="zero">Municípios sem perdas salvas saem com perda zero</Radio>
            </Space>
          </Radio.Group>
        </Space>
      </Card>

      <Card
        title="3. Conferir e gerar"
        extra={
          <Button icon={<FileSearchOutlined />} onClick={conferir} loading={conferindo} disabled={!podeConferir}>
            Conferir
          </Button>
        }
      >
        {!conferencia ? (
          <Text type="secondary">Confira os municípios selecionados antes de gerar.</Text>
        ) : (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {semPerdasCount > 0 && (
              <Alert
                type="warning"
                showIcon
                message={`${semPerdasCount} município(s) sem perdas salvas nesta competência`}
                description={
                  semPerdas === 'ignorar'
                    ? 'Eles ficarão de fora. Para incluí-los, salve as perdas no Dashboard ou escolha "saem com perda zero".'
                    : 'Os relatórios deles vão mostrar perda zero.'
                }
              />
            )}
            <Table
              size="small"
              rowKey="codigo_ibge"
              columns={colunas}
              dataSource={conferencia}
              pagination={{ pageSize: 20, hideOnSinglePage: true }}
              scroll={{ x: 700 }}
            />
            <Space wrap>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={gerar}
                loading={gerando}
                disabled={!tipos.length || aGerar === 0 || gerando}
              >
                Gerar {aGerar * tipos.length} relatório(s)
              </Button>
              {!tipos.length && <Text type="danger">Escolha ao menos um tipo de relatório.</Text>}
            </Space>
          </Space>
        )}

        {lote && (
          <Space direction="vertical" size="small" style={{ width: '100%', marginTop: 16 }}>
            <Progress
              percent={lote.total ? Math.round((lote.processados / lote.total) * 100) : 0}
              status={lote.status === 'erro' ? 'exception' : lote.status === 'concluido' ? 'success' : 'active'}
            />
            <Text>
              {lote.processados} de {lote.total} municípios processados · {lote.arquivos} arquivo(s)
            </Text>
            {lote.status === 'concluido' && lote.arquivos > 0 && (
              <Button icon={<CheckCircleOutlined />} onClick={baixarNovamente}>
                Baixar o ZIP novamente
              </Button>
            )}
            {lote.erros.length > 0 && (
              <Alert
                type={lote.status === 'erro' ? 'error' : 'info'}
                showIcon
                message="Avisos (também estão no erros.txt do ZIP)"
                description={
                  <ul style={{ margin: 0, paddingLeft: 18 }}>
                    {lote.erros.map((e) => <li key={e}>{e}</li>)}
                  </ul>
                }
              />
            )}
          </Space>
        )}
      </Card>
    </Space>
  );
};

export default RelatoriosLote;
