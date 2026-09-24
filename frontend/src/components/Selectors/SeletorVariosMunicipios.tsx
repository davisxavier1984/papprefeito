/**
 * Seleção de vários municípios (entre UFs) e competência.
 * Usado em Relatórios em lote.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Button, Input, Select, Space, Tag, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { apiClient, queryKeys } from '../../services/api';
import type { MunicipioLote } from '../../types';
import { competenciaValida, ordenarMunicipios } from '../../utils/municipiosLote';

const { Text } = Typography;

interface Props {
  selecionados: Record<string, MunicipioLote>;
  onChange: (selecionados: Record<string, MunicipioLote>) => void;
  competencia: string;
  onCompetenciaChange: (competencia: string) => void;
}

const SeletorVariosMunicipios: React.FC<Props> = ({ selecionados, onChange, competencia, onCompetenciaChange }) => {
  const [uf, setUf] = useState<string | undefined>();

  const { data: ufs = [], isLoading: carregandoUfs } = useQuery({
    queryKey: queryKeys.ufs,
    queryFn: () => apiClient.getUFs(),
    staleTime: 1000 * 60 * 60,
  });

  const { data: municipios = [], isLoading: carregandoMunicipios } = useQuery({
    queryKey: queryKeys.municipios(uf ?? ''),
    queryFn: () => apiClient.getMunicipiosPorUF(uf!),
    enabled: !!uf,
    staleTime: 1000 * 60 * 60,
  });

  const { data: ultimaCompetencia } = useQuery({
    queryKey: queryKeys.competencia,
    queryFn: () => apiClient.getUltimaCompetencia(),
    staleTime: 1000 * 60 * 10,
  });

  // Sugere a última competência uma única vez; depois o usuário pode apagar e digitar outra
  const competenciaSugeridaRef = useRef(false);
  useEffect(() => {
    if (competenciaSugeridaRef.current || !ultimaCompetencia?.competencia) return;
    competenciaSugeridaRef.current = true;
    if (!competencia) onCompetenciaChange(ultimaCompetencia.competencia);
  }, [ultimaCompetencia, competencia, onCompetenciaChange]);

  const lista = useMemo(() => ordenarMunicipios(selecionados), [selecionados]);
  const valoresUfAtual = useMemo(() => lista.filter((m) => m.uf === uf).map((m) => m.codigo_ibge), [lista, uf]);

  const aoMudarSelecaoUf = (codigos: string[]) => {
    if (!uf) return;
    const novo = Object.fromEntries(Object.entries(selecionados).filter(([, m]) => m.uf !== uf));
    for (const codigo of codigos) {
      const m = municipios.find((x) => x.codigo_ibge === codigo);
      if (m) novo[codigo] = { codigo_ibge: m.codigo_ibge, nome: m.nome, uf };
    }
    onChange(novo);
  };

  const removerUf = (sigla: string) =>
    onChange(Object.fromEntries(Object.entries(selecionados).filter(([, m]) => m.uf !== sigla)));

  const porUf = useMemo(() => {
    const cont: Record<string, number> = {};
    for (const m of lista) cont[m.uf] = (cont[m.uf] ?? 0) + 1;
    return cont;
  }, [lista]);

  return (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      <Space wrap>
        <Select
          placeholder="UF"
          style={{ width: 120 }}
          loading={carregandoUfs}
          value={uf}
          onChange={setUf}
          showSearch
          options={ufs.map((u) => ({ value: u.sigla, label: u.sigla }))}
        />
        <Button onClick={() => aoMudarSelecaoUf(municipios.map((m) => m.codigo_ibge))} disabled={!uf || !municipios.length}>
          Selecionar todos da UF
        </Button>
        <Input
          addonBefore="Competência"
          placeholder="AAAAMM"
          style={{ width: 220 }}
          value={competencia}
          maxLength={6}
          status={competencia && !competenciaValida(competencia) ? 'error' : undefined}
          onChange={(e) => onCompetenciaChange(e.target.value.replace(/\D/g, ''))}
        />
      </Space>

      <Select
        mode="multiple"
        placeholder={uf ? 'Busque e selecione os municípios' : 'Escolha a UF primeiro'}
        style={{ width: '100%' }}
        disabled={!uf}
        loading={carregandoMunicipios}
        value={valoresUfAtual}
        onChange={aoMudarSelecaoUf}
        optionFilterProp="label"
        maxTagCount="responsive"
        options={municipios.map((m) => ({ value: m.codigo_ibge, label: m.nome }))}
      />

      <Space wrap>
        <Text strong>{lista.length} município(s) selecionado(s)</Text>
        {Object.entries(porUf).map(([sigla, n]) => (
          <Tag key={sigla} closable onClose={() => removerUf(sigla)}>
            {sigla}: {n}
          </Tag>
        ))}
        {lista.length > 0 && (
          <Button type="link" size="small" onClick={() => onChange({})}>
            Limpar seleção
          </Button>
        )}
      </Space>
    </Space>
  );
};

export default SeletorVariosMunicipios;
