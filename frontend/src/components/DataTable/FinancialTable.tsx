/**
 * Componente: FinancialTable
 * - Tabela editável de simulação de impacto financeiro
 * - Para linhas com componentes SIAPS (eSF/eAP, Saúde Bucal, eMulti): a perda é decomposta
 *   em dois campos editáveis — "Vínculo e Acompanhamento" (CVAT) e "Qualidade" — com a base
 *   atual exibida como contexto (o ganho é adicional ao recebido, sem duplicar).
 * - Botão "Autopreencher" pré-preenche esses campos com a lacuna potencial do SIAPS.
 * - Demais linhas mantêm o campo único "Perda Recurso Mensal".
 * - Cálculos reativos + auto-save com debounce.
 */

import React, { useMemo } from 'react';
import { Table, Typography, Space, Tag, Card, Row, Col, Statistic, Divider, Button, Tooltip } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useMunicipioStore, useUpdatePerdaRecurso } from '../../stores/municipioStore';
import type { DadosProcessados } from '../../types';
import useAutoSave from '../../hooks/useAutoSave';
import { useIsMobile } from '../../hooks/useIsMobile';
import CurrencyInput from '../inputs/CurrencyInput';
import { sugestoesPorComponente, basePorComponente } from '../../utils/siaps';
import { formatCurrencyBRL as formatCurrency } from '../../utils/formatCurrency';

const { Text } = Typography;

const FinancialTable: React.FC = () => {
  const {
    dadosProcessados,
    dadosEditados,
    dadosFinanciamento,
    isLoading,
    siapsGap,
    siapsLoading,
    updatePerdaComponente,
    autopreencherSiaps,
  } = useMunicipioStore();
  const updatePerca = useUpdatePerdaRecurso();
  const { triggerSave, status, isSaving, isSaved, isError } = useAutoSave(2000);
  const isMobile = useIsMobile();

  const pagamento = dadosFinanciamento?.pagamentos?.[0];
  const recursos = useMemo(() => dadosProcessados.map((d) => d.recurso), [dadosProcessados]);

  // Lacuna potencial por componente (null = componente não se aplica àquela linha).
  const componentes = useMemo(
    () => sugestoesPorComponente(siapsGap, recursos),
    [siapsGap, recursos]
  );
  // Valor atual de cada componente (contexto), lido do pagamento.
  const bases = useMemo(() => basePorComponente(pagamento, recursos), [pagamento, recursos]);

  const isSiapsRow = (index: number) =>
    componentes[index]?.vinculo != null || componentes[index]?.qualidade != null;

  const temSiaps = !!siapsGap && componentes.some((c) => c.vinculo != null || c.qualidade != null);

  const handleAutopreencher = () => {
    autopreencherSiaps();
    triggerSave();
  };

  const setComponente = (index: number, comp: 'vinculo' | 'qualidade', val: number) => {
    const sanitized = Number.isFinite(val) && val >= 0 ? val : 0;
    updatePerdaComponente(index, comp, sanitized);
    triggerSave();
  };

  // Render de um input de componente (Vínculo/Qualidade) com a base atual abaixo.
  const renderComponente = (index: number, comp: 'vinculo' | 'qualidade', keyPrefix: string) => {
    const aplicavel = comp === 'vinculo'
      ? componentes[index]?.vinculo != null
      : componentes[index]?.qualidade != null;
    if (!aplicavel) {
      return <Text type="secondary">—</Text>;
    }
    const value =
      (comp === 'vinculo'
        ? dadosEditados?.perda_vinculo_mensal?.[index]
        : dadosEditados?.perda_qualidade_mensal?.[index]) ?? 0;
    const base = comp === 'vinculo' ? bases[index]?.vinculo : bases[index]?.qualidade;
    return (
      <div>
        <CurrencyInput
          id={`${keyPrefix}-${comp}-${index}`}
          name={`${keyPrefix}_${comp}_${index}`}
          value={value}
          onCommit={(val) => setComponente(index, comp, val)}
        />
        {base != null && (
          <Text
            type="secondary"
            style={{ fontSize: '11px', display: 'block', marginTop: '2px', textAlign: 'right' }}
          >
            atual: {formatCurrency(base)}
          </Text>
        )}
      </div>
    );
  };

  const componentColumns: ColumnsType<DadosProcessados & { key: number }> = [
    {
      title: (
        <Tooltip title="Ganho mensal projetado no componente Vínculo e Acompanhamento (CVAT). Adicional ao que já é recebido — não duplica o repasse atual.">
          Vínculo e Acompanhamento
        </Tooltip>
      ),
      key: 'perda_vinculo',
      align: 'right',
      width: 200,
      render: (_value: unknown, _record, index) => renderComponente(index, 'vinculo', 'perda-vinculo'),
    },
    {
      title: (
        <Tooltip title="Ganho mensal projetado no componente Qualidade. Adicional ao que já é recebido — não duplica o repasse atual.">
          Qualidade
        </Tooltip>
      ),
      key: 'perda_qualidade',
      align: 'right',
      width: 200,
      render: (_value: unknown, _record, index) => renderComponente(index, 'qualidade', 'perda-qualidade'),
    },
  ];

  const perdaColumn: ColumnsType<DadosProcessados & { key: number }>[number] = {
    title: temSiaps ? 'Perda Mensal (total)' : 'Perda Recurso Mensal',
    dataIndex: 'perda_recurso_mensal',
    key: 'perda_recurso_mensal',
    align: 'right',
    width: temSiaps ? 160 : 240,
    render: (_value: number, _record, index) => {
      if (isSiapsRow(index)) {
        // Total derivado (Vínculo + Qualidade) — somente leitura.
        return (
          <Tooltip title="Soma de Vínculo e Acompanhamento + Qualidade">
            <Text strong>{formatCurrency(dadosProcessados[index]?.perda_recurso_mensal ?? 0)}</Text>
          </Tooltip>
        );
      }
      return (
        <CurrencyInput
          id={`perda-recurso-${index}`}
          name={`perda_recurso_mensal_${index}`}
          value={dadosProcessados[index]?.perda_recurso_mensal ?? 0}
          onCommit={(val) => {
            const sanitized = Number.isFinite(val) && val >= 0 ? val : 0;
            updatePerca(index, sanitized);
            triggerSave();
          }}
        />
      );
    },
  };

  const columns: ColumnsType<DadosProcessados & { key: number }> = useMemo(() => {
    const cols: ColumnsType<DadosProcessados & { key: number }> = [
      {
        title: 'Recurso',
        dataIndex: 'recurso',
        key: 'recurso',
        width: 240,
        render: (text: string) => <Text strong>{text}</Text>,
      },
      {
        title: 'Recebido Mensal',
        dataIndex: 'recurso_real',
        key: 'recurso_real',
        align: 'right',
        width: 160,
        render: (value: number) => <Text>{formatCurrency(value)}</Text>,
      },
      ...(temSiaps ? componentColumns : []),
      perdaColumn,
      {
        title: 'Potencial Mensal',
        dataIndex: 'recurso_potencial',
        key: 'recurso_potencial',
        align: 'right',
        width: 160,
        render: (value: number) => <Text>{formatCurrency(value)}</Text>,
      },
      {
        title: 'Recebido Anual',
        dataIndex: 'recurso_real_anual',
        key: 'recurso_real_anual',
        align: 'right',
        width: 160,
        render: (value: number) => <Text>{formatCurrency(value)}</Text>,
      },
      {
        title: 'Potencial Anual',
        dataIndex: 'recurso_potencial_anual',
        key: 'recurso_potencial_anual',
        align: 'right',
        width: 170,
        render: (value: number) => <Text>{formatCurrency(value)}</Text>,
      },
      {
        title: 'Diferença Anual',
        dataIndex: 'diferenca',
        key: 'diferenca',
        align: 'right',
        width: 160,
        render: (value: number) => (
          <Text type={value > 0 ? 'success' : value < 0 ? 'danger' : undefined}>
            {formatCurrency(value)}
          </Text>
        ),
      },
    ];
    return cols;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dadosProcessados, dadosEditados, componentes, bases, temSiaps, triggerSave, updatePerca]);

  const dataSource = useMemo(
    () => dadosProcessados.map((row, idx) => ({ key: idx, ...row })),
    [dadosProcessados]
  );

  // Barra de Autopreencher SIAPS (substitui a antiga barra com Segmented que sumia).
  const siapsBar = (siapsLoading || temSiaps) && (
    <Space size="small" wrap style={{ width: '100%' }}>
      <Tooltip title="Preenche Vínculo e Acompanhamento + Qualidade com o ganho do SIAPS: quanto a mais o município receberia se todas as equipes chegassem a Ótimo, comparado ao que é pago hoje. Você pode ajustar os valores depois.">
        <Button
          type="primary"
          ghost
          icon={<ThunderboltOutlined />}
          loading={siapsLoading}
          disabled={!temSiaps}
          onClick={handleAutopreencher}
        >
          Autopreencher com SIAPS
        </Button>
      </Tooltip>
      {siapsLoading && <Tag color="processing">Carregando classificação…</Tag>}
      {temSiaps && (
        <>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            ganho se todas as equipes chegarem a “Ótimo” (vs. o pago hoje)
          </Text>
          {siapsGap?.quadrimestre_aplicado && (
            <Tag color="blue">Quadrimestre {siapsGap.quadrimestre_aplicado}</Tag>
          )}
          {siapsGap && !siapsGap.valores_validados && (
            <Tooltip title="Os valores de referência por classificação/estrato ainda estão em validação.">
              <Tag color="warning">valores provisórios</Tag>
            </Tooltip>
          )}
        </>
      )}
    </Space>
  );

  // Componente para visualização mobile em cards
  const MobileCardView = () => (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      {dadosProcessados.map((item, index) => (
        <Card
          key={index}
          className="shadow-brand"
          style={{
            borderRadius: '12px',
            border: '1px solid var(--border-color)'
          }}
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Text strong style={{ fontSize: '16px', color: 'var(--text-primary)' }}>
                {item.recurso}
              </Text>
            </div>

            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic
                  title="Recebido Mensal"
                  value={item.recurso_real}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '14px', color: 'var(--primary-blue)' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Potencial Mensal"
                  value={item.recurso_potencial}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '14px', color: 'var(--success-green)' }}
                />
              </Col>
            </Row>

            <Divider style={{ margin: '8px 0' }} />

            {isSiapsRow(index) ? (
              <div>
                {componentes[index]?.vinculo != null && (
                  <div style={{ marginBottom: '8px' }}>
                    <Text type="secondary" style={{ fontSize: '13px', fontWeight: 500 }}>
                      Vínculo e Acompanhamento:
                    </Text>
                    <div style={{ marginTop: '4px' }}>
                      {renderComponente(index, 'vinculo', 'perda-vinculo-mobile')}
                    </div>
                  </div>
                )}
                {componentes[index]?.qualidade != null && (
                  <div style={{ marginBottom: '8px' }}>
                    <Text type="secondary" style={{ fontSize: '13px', fontWeight: 500 }}>
                      Qualidade:
                    </Text>
                    <div style={{ marginTop: '4px' }}>
                      {renderComponente(index, 'qualidade', 'perda-qualidade-mobile')}
                    </div>
                  </div>
                )}
                <Text type="secondary" style={{ fontSize: '13px' }}>
                  Perda mensal (total):{' '}
                  <Text strong>{formatCurrency(item.perda_recurso_mensal ?? 0)}</Text>
                </Text>
              </div>
            ) : (
              <div>
                <Text type="secondary" style={{ fontSize: '13px', fontWeight: 500 }}>
                  Perda Recurso Mensal:
                </Text>
                <div style={{ marginTop: '4px' }}>
                  <CurrencyInput
                    id={`perda-recurso-mobile-${index}`}
                    name={`perda_recurso_mensal_mobile_${index}`}
                    value={item.perda_recurso_mensal ?? 0}
                    onCommit={(val) => {
                      const sanitized = Number.isFinite(val) && val >= 0 ? val : 0;
                      updatePerca(index, sanitized);
                      triggerSave();
                    }}
                  />
                </div>
              </div>
            )}

            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic
                  title="Recebido Anual"
                  value={item.recurso_real_anual}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '13px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="Potencial Anual"
                  value={item.recurso_potencial_anual}
                  formatter={(v) => formatCurrency(Number(v))}
                  style={{ textAlign: 'center' }}
                  valueStyle={{ fontSize: '13px' }}
                />
              </Col>
            </Row>

            <div style={{ textAlign: 'center', marginTop: '8px' }}>
              <Tag
                color={item.diferenca > 0 ? 'success' : item.diferenca < 0 ? 'error' : 'default'}
                style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  padding: '4px 12px',
                  borderRadius: '6px'
                }}
              >
                Diferença: {formatCurrency(item.diferenca)}
              </Tag>
            </div>
          </Space>
        </Card>
      ))}
    </Space>
  );

  return (
    <Space direction="vertical" size="small" style={{ width: '100%' }}>
      <Space size="small" style={{ justifyContent: 'space-between', width: '100%' }}>
        <Space size="small">
          <Text type="secondary" style={{ fontSize: '13px' }}>Status:</Text>
          {isSaving && <Tag color="processing">Salvando...</Tag>}
          {isSaved && status === 'saved' && <Tag color="success">Salvo</Tag>}
          {isError && <Tag color="error">Erro ao salvar</Tag>}
          {!isSaving && !isSaved && !isError && <Tag>Pronto</Tag>}
        </Space>
        {!isMobile && (
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {dadosProcessados.length} registros
          </Text>
        )}
      </Space>

      {siapsBar}

      {isMobile ? (
        <MobileCardView />
      ) : (
        <Table
          size="middle"
          bordered
          loading={isLoading}
          columns={columns}
          dataSource={dataSource}
          pagination={false}
          scroll={{ x: 1200 }}
          rowKey="key"
          style={{
            backgroundColor: 'var(--bg-container)',
            borderRadius: '12px',
            overflow: 'hidden'
          }}
        />
      )}
    </Space>
  );
};

export default FinancialTable;
