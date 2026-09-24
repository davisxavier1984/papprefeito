/**
 * Preenchimento automático (story 3.3)
 * Busca a sugestão calculada no backend, mostra os componentes de cada plano para
 * revisão e, só quando o usuário confirma, aplica os valores na tabela.
 * A digitação manual continua funcionando normalmente, antes e depois.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Checkbox, Empty, InputNumber, Modal, Space, Spin, Tag, Typography } from 'antd';
import { apiClient } from '../../services/api';
import { useMunicipioStore } from '../../stores/municipioStore';
import type { PlanoParecidos, PlanoSugestao, SugestaoAplicada } from '../../types';
import { REGRA_PARECIDOS, resumoParecidos } from '../../utils/parecidos';

const { Text } = Typography;

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const arred = (v: number) => Math.round(v * 100) / 100;

const TIPO_LABEL: Record<PlanoSugestao['tipo'], string> = {
  esf: 'eSF/eAP',
  acs: 'ACS',
  sb: 'Saúde Bucal',
  emulti: 'eMulti',
  outro: 'Sem regra',
};

const totalDoPlano = (plano: PlanoSugestao) =>
  Math.max(arred(plano.componentes.filter((c) => c.incluido).reduce((s, c) => s + c.quantidade * c.valor_unitario, 0)), 0);

interface Props {
  open: boolean;
  onClose: () => void;
  /** Chamado depois que os valores foram aplicados na store, para disparar o salvamento */
  onAplicado: () => void;
}

const PreenchimentoAutomatico: React.FC<Props> = ({ open, onClose, onAplicado }) => {
  const { selectedMunicipio, selectedCompetencia, dadosProcessados } = useMunicipioStore();
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [planos, setPlanos] = useState<PlanoSugestao[]>([]);
  const [selecionados, setSelecionados] = useState<Record<number, boolean>>({});
  const [parecidos, setParecidos] = useState<Record<number, PlanoParecidos>>({});
  const [usarMediana, setUsarMediana] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (!open || !selectedMunicipio?.codigo_ibge || !selectedCompetencia) return;
    // Cada abertura começa do zero: nada da busca anterior fica na tela se esta falhar
    let atual = true;
    setCarregando(true);
    setErro(null);
    setAviso(null);
    setPlanos([]);
    setSelecionados({});
    setParecidos({});
    setUsarMediana({});
    apiClient
      .getSugestaoPreenchimento(selectedMunicipio.codigo_ibge, selectedCompetencia)
      .then((r) => {
        if (!atual) return;
        setPlanos(r.planos);
        setAviso(r.aviso ?? null);
        setSelecionados(Object.fromEntries(r.planos.filter((p) => p.aplicavel).map((p) => [p.indice, true])));
      })
      .catch((e) => {
        if (atual) setErro(e?.message || 'Não foi possível calcular a sugestão.');
      })
      .finally(() => {
        if (atual) setCarregando(false);
      });
    // Municípios parecidos são um complemento; falha aqui não deve travar o modal
    apiClient
      .getParecidos(selectedMunicipio.codigo_ibge, selectedCompetencia)
      .then((r) => {
        if (atual) setParecidos(Object.fromEntries(r.planos.map((p) => [p.indice, p])));
      })
      .catch(() => undefined);
    return () => {
      atual = false;
    };
  }, [open, selectedMunicipio?.codigo_ibge, selectedCompetencia]);

  const alterarComponente = (indice: number, id: string, mudanca: { incluido?: boolean; quantidade?: number }) =>
    setPlanos((atual) =>
      atual.map((p) =>
        p.indice !== indice
          ? p
          : { ...p, componentes: p.componentes.map((c) => (c.id === id ? { ...c, ...mudanca } : c)) }
      )
    );

  const valorAtual = (indice: number) => dadosProcessados[indice]?.perda_recurso_mensal ?? 0;
  const aplicaveis = useMemo(() => planos.filter((p) => p.aplicavel && selecionados[p.indice]), [planos, selecionados]);
  const quantidadeAplicar =
    aplicaveis.length +
    Object.entries(usarMediana).filter(([i, u]) => u && parecidos[Number(i)]?.mediana != null).length;

  const aplicar = () => {
    const { dadosEditados, sugestoesAplicadas, setDadosEditados, setSugestoesAplicadas } =
      useMunicipioStore.getState();
    if (!dadosEditados) return;

    // Mesmo tamanho da tabela; posições sem regra mantêm o valor atual
    const perdas = dadosProcessados.map((d, i) => dadosEditados.perda_recurso_mensal?.[i] ?? d.perda_recurso_mensal ?? 0);
    const sugestoes: Record<number, SugestaoAplicada> = { ...sugestoesAplicadas };
    for (const p of aplicaveis) {
      if (p.indice >= perdas.length) continue;
      const total = totalDoPlano(p);
      perdas[p.indice] = total;
      sugestoes[p.indice] = {
        regra_id: p.regra_id ?? `${p.tipo}_v1`,
        valor_sugerido: p.total_sugerido,
        valor_aplicado: total,
      };
    }
    // Mediana dos municípios parecidos (Demais e Promoção), só onde o consultor escolheu usar
    for (const [indice, usar] of Object.entries(usarMediana)) {
      const i = Number(indice);
      const valor = parecidos[i]?.mediana;
      if (!usar || valor == null || i >= perdas.length) continue;
      perdas[i] = valor;
      sugestoes[i] = { regra_id: REGRA_PARECIDOS, valor_sugerido: valor, valor_aplicado: valor };
    }
    setSugestoesAplicadas(sugestoes);
    setDadosEditados({ ...dadosEditados, perda_recurso_mensal: perdas, data_edicao: new Date().toISOString() });
    onAplicado();
    onClose();
  };

  return (
    <Modal
      open={open}
      onCancel={onClose}
      width={920}
      title="Preencher automaticamente"
      footer={[
        <Button key="cancelar" onClick={onClose}>
          Cancelar
        </Button>,
        <Button key="aplicar" type="primary" onClick={aplicar} disabled={carregando || !quantidadeAplicar}>
          Aplicar {quantidadeAplicar} plano(s) na tabela
        </Button>,
      ]}
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Text type="secondary">
          Estimativa do que o município poderia receber, calculada com os dados do Ministério. Revise, ajuste as
          quantidades e escolha o que aplicar. Nada muda na tabela até você clicar em aplicar, e depois você pode
          editar qualquer valor normalmente.
        </Text>
        {aviso && <Alert type="warning" showIcon message={aviso} />}
        {erro && <Alert type="error" showIcon message={erro} />}
        {carregando ? (
          <div style={{ textAlign: 'center', padding: 32 }}>
            <Spin tip="Calculando a sugestão…">
              <div style={{ minHeight: 48 }} />
            </Spin>
          </div>
        ) : !erro && planos.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Nenhum plano com cálculo automático para este município." />
        ) : (
          planos.map((p) => {
            const total = totalDoPlano(p);
            return (
              <Card
                key={p.indice}
                size="small"
                title={
                  <Space wrap>
                    {p.aplicavel && (
                      <Checkbox
                        checked={!!selecionados[p.indice]}
                        onChange={(e) => setSelecionados((s) => ({ ...s, [p.indice]: e.target.checked }))}
                      />
                    )}
                    <Text strong>{p.plano}</Text>
                    <Tag>{TIPO_LABEL[p.tipo]}</Tag>
                  </Space>
                }
                extra={
                  p.aplicavel ? (
                    <Space>
                      <Text type="secondary">{moeda.format(valorAtual(p.indice))} →</Text>
                      <Text strong>{moeda.format(total)}</Text>
                    </Space>
                  ) : usarMediana[p.indice] ? (
                    <Space>
                      <Text type="secondary">{moeda.format(valorAtual(p.indice))} →</Text>
                      <Text strong>{moeda.format(parecidos[p.indice]?.mediana ?? 0)}</Text>
                    </Space>
                  ) : (
                    <Text type="secondary">mantém {moeda.format(valorAtual(p.indice))}</Text>
                  )
                }
              >
                {p.aplicavel ? (
                  <Space direction="vertical" size={6} style={{ width: '100%' }}>
                    {p.componentes.map((c) => (
                      <div key={c.id} style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                        <Checkbox
                          checked={c.incluido}
                          disabled={!selecionados[p.indice]}
                          onChange={(e) => alterarComponente(p.indice, c.id, { incluido: e.target.checked })}
                          style={{ minWidth: 300 }}
                        >
                          {c.nome}
                        </Checkbox>
                        {c.quantidade_editavel ? (
                          <InputNumber
                            size="small"
                            min={0}
                            precision={0}
                            value={c.quantidade}
                            disabled={!selecionados[p.indice] || !c.incluido}
                            onChange={(v) => alterarComponente(p.indice, c.id, { quantidade: Number(v ?? 0) })}
                            aria-label={`Quantidade: ${c.nome}`}
                            style={{ width: 80 }}
                          />
                        ) : (
                          <Text style={{ width: 80, display: 'inline-block' }}>{c.quantidade}</Text>
                        )}
                        <Text type="secondary">× {moeda.format(c.valor_unitario)}</Text>
                        <Text strong style={{ marginLeft: 'auto' }}>
                          {c.incluido ? moeda.format(c.quantidade * c.valor_unitario) : '—'}
                        </Text>
                        {c.detalhe && (
                          <Text type="secondary" style={{ width: '100%', fontSize: 12, paddingLeft: 24 }}>
                            {c.detalhe}
                          </Text>
                        )}
                      </div>
                    ))}
                  </Space>
                ) : (
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    <Text type="secondary">{p.observacao}</Text>
                    {parecidos[p.indice] &&
                      (parecidos[p.indice].exemplos.length ? (
                        <Space direction="vertical" size={4} style={{ width: '100%' }}>
                          <Text type="secondary">
                            Municípios parecidos: {resumoParecidos(parecidos[p.indice].exemplos, moeda)}
                          </Text>
                          <Checkbox
                            checked={!!usarMediana[p.indice]}
                            onChange={(e) => setUsarMediana((u) => ({ ...u, [p.indice]: e.target.checked }))}
                          >
                            Usar a mediana: {moeda.format(parecidos[p.indice].mediana ?? 0)}
                          </Checkbox>
                        </Space>
                      ) : (
                        <Text type="secondary">Sem histórico parecido.</Text>
                      ))}
                  </Space>
                )}
              </Card>
            );
          })
        )}
      </Space>
    </Modal>
  );
};

export default PreenchimentoAutomatico;
