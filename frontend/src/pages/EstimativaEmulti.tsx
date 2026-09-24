/**
 * Estimativa eMulti (story 3.6)
 * Módulo opcional: estima quantas eMulti cada município poderia ter pelos profissionais
 * elegíveis do CNES (Portaria 635/2023), para um ou vários municípios. Nada é gravado
 * até o usuário aplicar.
 */

import React, { useMemo, useRef, useState } from 'react';
import {
  Alert,
  App,
  Button,
  Card,
  Checkbox,
  InputNumber,
  Popconfirm,
  Progress,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { CalculatorOutlined, CheckOutlined, DownloadOutlined, StopOutlined } from '@ant-design/icons';
import { apiClient } from '../services/api';
import { useMunicipioStore } from '../stores/municipioStore';
import SeletorVariosMunicipios from '../components/Selectors/SeletorVariosMunicipios';
import { competenciaValida, ordenarMunicipios } from '../utils/municipiosLote';
import type { EstimativaEmulti as Estimativa, ModalidadeEmulti, MunicipioLote } from '../types';

const { Title, Text } = Typography;

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const MODALIDADES: { chave: ModalidadeEmulti; rotulo: string }[] = [
  { chave: 'estrategica', rotulo: 'Estratégica' },
  { chave: 'complementar', rotulo: 'Complementar' },
  { chave: 'ampliada', rotulo: 'Ampliada' },
];
const REGRA_ID = 'emulti_estimativa_v1';

interface Linha extends MunicipioLote {
  estado: 'aguardando' | 'ok' | 'erro';
  mensagem?: string;
  estimativa?: Estimativa;
  combinacao?: Record<ModalidadeEmulti, number>;
  aplicado?: { ok: boolean; mensagem: string };
}

const custeioDe = (e: Estimativa, comb: Record<ModalidadeEmulti, number>) =>
  MODALIDADES.reduce((s, m) => s + (comb[m.chave] ?? 0) * e.custeio_modalidade[m.chave], 0);

const EstimativaEmulti: React.FC = () => {
  const { message } = App.useApp();
  const [selecionados, setSelecionados] = useState<Record<string, MunicipioLote>>({});
  const [competencia, setCompetencia] = useState('');
  const [divisor, setDivisor] = useState<number | null>(null);
  const [comQualidade, setComQualidade] = useState(false);
  const [linhas, setLinhas] = useState<Linha[]>([]);
  const [estimando, setEstimando] = useState(false);
  const [aplicando, setAplicando] = useState(false);
  const [marcadas, setMarcadas] = useState<React.Key[]>([]);
  const cancelarRef = useRef(false);

  const lista = useMemo(() => ordenarMunicipios(selecionados), [selecionados]);
  const feitas = linhas.filter((l) => l.estado !== 'aguardando').length;

  const fatorQualidade = (e: Estimativa) => (comQualidade ? 1 + e.qualidade_pct : 1);
  const perdaDe = (l: Linha) =>
    l.estimativa && l.combinacao
      ? Math.round(Math.max(custeioDe(l.estimativa, l.combinacao) - l.estimativa.custeio_atual, 0) * fatorQualidade(l.estimativa) * 100) / 100
      : 0;
  const sugeridoDe = (e: Estimativa) => Math.round(e.perda_estimada * fatorQualidade(e) * 100) / 100;

  const atualizar = (codigo: string, mudanca: Partial<Linha>) =>
    setLinhas((atual) => atual.map((l) => (l.codigo_ibge === codigo ? { ...l, ...mudanca } : l)));

  const estimar = async () => {
    cancelarRef.current = false;
    setEstimando(true);
    setMarcadas([]);
    setLinhas(lista.map((m) => ({ ...m, estado: 'aguardando' })));
    // Um município por vez: a coleta do CNES é pesada e assim o progresso fica visível
    for (const m of lista) {
      if (cancelarRef.current) break;
      try {
        const e = await apiClient.getEstimativaEmulti(m.codigo_ibge, competencia, divisor ?? undefined);
        atualizar(m.codigo_ibge, { estado: 'ok', estimativa: e, combinacao: { ...e.combinacao } });
        setMarcadas((k) => [...k, m.codigo_ibge]);
      } catch (err) {
        atualizar(m.codigo_ibge, { estado: 'erro', mensagem: (err as { message?: string })?.message || 'Erro' });
      }
    }
    setEstimando(false);
  };

  const aplicar = async () => {
    const alvo = linhas.filter((l) => l.estado === 'ok' && marcadas.includes(l.codigo_ibge));
    if (!alvo.length) return;
    setAplicando(true);
    try {
      const itens = alvo.map((l) => ({
        codigo_ibge: l.codigo_ibge,
        valor: perdaDe(l),
        valor_sugerido: sugeridoDe(l.estimativa!),
      }));
      const resultados = await apiClient.aplicarEmulti(competencia, itens);
      resultados.forEach((r) => atualizar(r.codigo_ibge, { aplicado: { ok: r.ok, mensagem: r.mensagem } }));
      const ok = resultados.filter((r) => r.ok).length;
      if (ok) message.success(`eMulti gravada em ${ok} município(s).`);
      if (ok < resultados.length) message.warning(`${resultados.length - ok} município(s) não foram gravados. Veja a coluna Situação.`);

      // Se o município aberto no Dashboard foi alterado, atualiza a tabela dele para
      // que um salvamento posterior lá não sobrescreva o valor gravado aqui
      const store = useMunicipioStore.getState();
      const aberto = store.selectedMunicipio?.codigo_ibge;
      const alterado = alvo.find(
        (l) => l.codigo_ibge === aberto && resultados.find((r) => r.codigo_ibge === aberto)?.ok
      );
      if (alterado && store.selectedCompetencia === competencia && store.dadosEditados && alterado.estimativa?.indice_plano != null) {
        const i = alterado.estimativa.indice_plano;
        const perdas = [...store.dadosEditados.perda_recurso_mensal];
        const valor = perdaDe(alterado);
        if (i < perdas.length) {
          perdas[i] = valor;
          store.setSugestoesAplicadas({
            ...store.sugestoesAplicadas,
            [i]: { regra_id: REGRA_ID, valor_sugerido: sugeridoDe(alterado.estimativa), valor_aplicado: valor },
          });
          store.setDadosEditados({ ...store.dadosEditados, perda_recurso_mensal: perdas });
        }
      }
    } catch {
      message.error('Não foi possível gravar as estimativas.');
    } finally {
      setAplicando(false);
    }
  };

  const exportarCsv = () => {
    const cab = ['UF', 'Município', 'Código IBGE', 'eSF+eAP', 'eMulti atuais (E/C/A)', 'Profissionais elegíveis',
      'Nutricionistas+psicólogos', 'Equipes estimadas', 'Combinação (E/C/A)', 'Custeio atual', 'Perda estimada'];
    const lin = linhas.filter((l) => l.estado === 'ok').map((l) => {
      const e = l.estimativa!;
      const c = l.combinacao!;
      return [l.uf, l.nome, l.codigo_ibge, e.equipes_aps, `${e.atuais.estrategica}/${e.atuais.complementar}/${e.atuais.ampliada}`,
        e.profissionais_elegiveis, e.nutricionistas_psicologos, e.equipes_estimadas,
        `${c.estrategica}/${c.complementar}/${c.ampliada}`, e.custeio_atual.toFixed(2).replace('.', ','),
        perdaDe(l).toFixed(2).replace('.', ',')];
    });
    const csv = [cab, ...lin].map((r) => r.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')).join('\n');
    const url = URL.createObjectURL(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `estimativa_emulti_${competencia}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const colunas: ColumnsType<Linha> = [
    {
      title: 'Município',
      key: 'municipio',
      render: (_, l) => (
        <Space direction="vertical" size={0}>
          <Text strong>{l.nome}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{l.uf} · {l.codigo_ibge}</Text>
        </Space>
      ),
    },
    {
      title: 'eSF + eAP',
      key: 't',
      width: 90,
      align: 'center',
      render: (_, l) => l.estimativa?.equipes_aps ?? '—',
    },
    {
      title: 'eMulti atuais (E/C/A)',
      key: 'atuais',
      width: 120,
      align: 'center',
      render: (_, l) => (l.estimativa ? `${l.estimativa.atuais.estrategica}/${l.estimativa.atuais.complementar}/${l.estimativa.atuais.ampliada}` : '—'),
    },
    {
      title: 'Elegíveis (nutri+psi)',
      key: 'p',
      width: 130,
      align: 'center',
      render: (_, l) => (l.estimativa ? `${l.estimativa.profissionais_elegiveis} (${l.estimativa.nutricionistas_psicologos})` : '—'),
    },
    {
      title: 'Combinação alvo (E / C / A)',
      key: 'combinacao',
      width: 230,
      render: (_, l) =>
        l.estimativa && l.combinacao ? (
          <Space size={4}>
            {MODALIDADES.map((m) => (
              <InputNumber
                key={m.chave}
                size="small"
                min={0}
                precision={0}
                value={l.combinacao![m.chave]}
                style={{ width: 60 }}
                aria-label={`${m.rotulo}: ${l.nome}`}
                onChange={(v) => atualizar(l.codigo_ibge, { combinacao: { ...l.combinacao!, [m.chave]: Number(v ?? 0) } })}
              />
            ))}
          </Space>
        ) : '—',
    },
    {
      title: 'Perda estimada',
      key: 'perda',
      width: 140,
      align: 'right',
      render: (_, l) => (l.estado === 'ok' ? <Text strong>{moeda.format(perdaDe(l))}</Text> : '—'),
    },
    {
      title: 'Situação',
      key: 'estado',
      width: 170,
      render: (_, l) => {
        if (l.aplicado) return <Tag color={l.aplicado.ok ? 'green' : 'red'}>{l.aplicado.ok ? 'Gravado' : l.aplicado.mensagem}</Tag>;
        if (l.estado === 'aguardando') return <Tag>{estimando ? 'Na fila' : 'Não estimado'}</Tag>;
        if (l.estado === 'erro') return <Tag color="red">{l.mensagem}</Tag>;
        return l.estimativa?.aviso ? <Tag color="orange">Conferir</Tag> : <Tag color="blue">Estimado</Tag>;
      },
    },
  ];

  const linhaExpandida = (l: Linha) => {
    const e = l.estimativa;
    if (!e) return null;
    return (
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        {e.aviso && <Alert type="warning" showIcon message={e.aviso} />}
        <Text type="secondary">
          Cálculo: mín(eSF + eAP = {e.equipes_aps}; elegíveis ÷ {e.divisor} = {Math.floor(e.profissionais_elegiveis / e.divisor)};
          nutricionistas + psicólogos = {e.nutricionistas_psicologos}) = <Text strong>{e.equipes_estimadas}</Text> eMulti.
          Teto do Ministério (E/C/A): {e.teto.estrategica}/{e.teto.complementar}/{e.teto.ampliada}. Custeio atual: {moeda.format(e.custeio_atual)}.
          Faixas da Portaria 635/2023: Estratégica 1–4, Complementar 5–9, Ampliada 10–12 eSF/eAP vinculadas.
        </Text>
        <Space wrap>
          {e.profissionais.map((p) => (
            <Tag key={p.cbo} color={p.composicao_fixa ? 'geekblue' : undefined}>
              {p.categoria}: {p.pessoas}
            </Tag>
          ))}
          {!e.profissionais.length && <Text type="secondary">Nenhum profissional elegível no CNES.</Text>}
        </Space>
      </Space>
    );
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={3} style={{ marginBottom: 4 }}>Estimativa eMulti</Title>
        <Text type="secondary">
          Módulo opcional. Estima quantas eMulti cada município poderia ter pelos profissionais elegíveis cadastrados no
          CNES. Nada é gravado até você aplicar, e depois você ainda pode editar o valor no Dashboard.
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

      <Card
        title="2. Estimar"
        extra={
          <Space>
            {estimando ? (
              <Button icon={<StopOutlined />} onClick={() => (cancelarRef.current = true)}>
                Parar
              </Button>
            ) : (
              <Button
                type="primary"
                icon={<CalculatorOutlined />}
                onClick={estimar}
                disabled={!lista.length || !competenciaValida(competencia)}
              >
                Estimar {lista.length} município(s)
              </Button>
            )}
          </Space>
        }
      >
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Space wrap>
            <Text>Profissionais elegíveis por equipe:</Text>
            <InputNumber min={1} max={50} value={divisor} onChange={(v) => setDivisor(v)} placeholder="6 (padrão)" style={{ width: 120 }} />
            <Checkbox checked={comQualidade} onChange={(e) => setComQualidade(e.target.checked)}>
              Incluir qualidade BOM (+18,75% do custeio)
            </Checkbox>
          </Space>
          {linhas.length > 0 && (
            <Progress percent={Math.round((feitas / linhas.length) * 100)} status={estimando ? 'active' : undefined} />
          )}
          {linhas.length > 0 && (
            <Table
              size="small"
              rowKey="codigo_ibge"
              columns={colunas}
              dataSource={linhas}
              pagination={{ pageSize: 20, hideOnSinglePage: true }}
              scroll={{ x: 1000 }}
              expandable={{ expandedRowRender: linhaExpandida, rowExpandable: (l) => l.estado === 'ok' }}
              rowSelection={{
                selectedRowKeys: marcadas,
                onChange: setMarcadas,
                getCheckboxProps: (l) => ({ disabled: l.estado !== 'ok' }),
              }}
            />
          )}
          {linhas.some((l) => l.estado === 'ok') && !estimando && (
            <Space wrap>
              <Popconfirm
                title="Gravar a perda da eMulti destes municípios?"
                description="O valor salvo na posição da eMulti será substituído. As outras perdas não mudam."
                onConfirm={aplicar}
                okText="Gravar"
                cancelText="Cancelar"
              >
                <Button type="primary" icon={<CheckOutlined />} loading={aplicando} disabled={!marcadas.length}>
                  Aplicar em {marcadas.length} município(s)
                </Button>
              </Popconfirm>
              <Button icon={<DownloadOutlined />} onClick={exportarCsv}>
                Exportar planilha (CSV)
              </Button>
            </Space>
          )}
        </Space>
      </Card>
    </Space>
  );
};

export default EstimativaEmulti;
