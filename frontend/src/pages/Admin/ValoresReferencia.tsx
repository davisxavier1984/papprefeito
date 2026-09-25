/**
 * Valores de referência do financiamento federal por vigência (story 3.3)
 * Usados pelo preenchimento automático. Só administradores alteram.
 */

import React, { useMemo, useState } from 'react';
import { Alert, App, Button, Card, Form, Input, InputNumber, Popconfirm, Select, Space, Table, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import type { ValorReferencia, ValorReferenciaCreate } from '../../types';

const { Title, Text } = Typography;

const VIGENCIA_INICIAL = '202405';
const numero = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtVigencia = (v: string) => `${v.slice(4)}/${v.slice(0, 4)}`;

const ValoresReferencia: React.FC = () => {
  const { message } = App.useApp();
  const queryClient = useQueryClient();
  const [form] = Form.useForm<ValorReferenciaCreate>();
  const [filtro, setFiltro] = useState('');

  const { data: valores = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['valores-referencia'],
    queryFn: () => apiClient.listarValoresReferencia(),
  });

  const chaves = useMemo(() => {
    const m = new Map<string, string>();
    valores.forEach((v) => m.set(v.chave, v.descricao));
    return [...m.entries()].map(([value, label]) => ({ value, label }));
  }, [valores]);

  const cadastrar = useMutation({
    mutationFn: (dados: ValorReferenciaCreate) => apiClient.cadastrarValorReferencia(dados),
    onSuccess: () => {
      message.success('Valor cadastrado.');
      form.resetFields(['valor', 'fonte']);
      queryClient.invalidateQueries({ queryKey: ['valores-referencia'] });
    },
    onError: (e: { message?: string }) => message.error(e?.message || 'Não foi possível cadastrar.'),
  });

  const remover = useMutation({
    mutationFn: (id: number) => apiClient.removerValorReferencia(id),
    onSuccess: () => {
      message.success('Vigência removida.');
      queryClient.invalidateQueries({ queryKey: ['valores-referencia'] });
    },
    onError: (e: { message?: string }) => message.error(e?.message || 'Não foi possível remover.'),
  });

  const filtrados = valores.filter(
    (v) => !filtro || `${v.descricao} ${v.chave}`.toLowerCase().includes(filtro.toLowerCase())
  );

  const colunas: ColumnsType<ValorReferencia> = [
    { title: 'Parâmetro', dataIndex: 'descricao', key: 'descricao' },
    {
      title: 'Vigente desde',
      dataIndex: 'vigente_desde',
      key: 'vigente_desde',
      width: 130,
      render: (v: string) => fmtVigencia(v),
    },
    {
      title: 'Valor',
      dataIndex: 'valor',
      key: 'valor',
      align: 'right',
      width: 140,
      render: (v: number) => numero.format(v),
    },
    { title: 'Fonte', dataIndex: 'fonte', key: 'fonte', render: (f?: string | null) => <Text type="secondary">{f}</Text> },
    {
      title: '',
      key: 'acoes',
      width: 60,
      render: (_, r) =>
        r.vigente_desde !== VIGENCIA_INICIAL && (
          <Popconfirm title="Remover esta vigência?" onConfirm={() => remover.mutate(r.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} aria-label="Remover vigência" />
          </Popconfirm>
        ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={3} style={{ marginBottom: 4 }}>Valores de referência</Title>
        <Text type="secondary">
          Valores do financiamento federal usados no preenchimento automático. Cada valor vale a partir da
          competência informada, até a próxima vigência do mesmo parâmetro.
        </Text>
      </div>

      <Alert
        type="info"
        showIcon
        message="Os valores iniciais foram conferidos com os pagamentos de 2025. Para 2026, cadastre os valores da portaria vigente (Portaria GM/MS 10.994/2026)."
      />

      <Card title="Cadastrar nova vigência">
        <Form
          form={form}
          layout="inline"
          onFinish={(v) => cadastrar.mutate(v)}
          style={{ rowGap: 12 }}
        >
          <Form.Item name="chave" rules={[{ required: true, message: 'Escolha o parâmetro' }]}>
            <Select placeholder="Parâmetro" options={chaves} style={{ width: 360 }} showSearch optionFilterProp="label" />
          </Form.Item>
          <Form.Item
            name="vigente_desde"
            rules={[{ required: true, pattern: /^\d{4}(0[1-9]|1[0-2])$/, message: 'AAAAMM' }]}
          >
            <Input placeholder="Vigente desde (AAAAMM)" style={{ width: 190 }} maxLength={6} />
          </Form.Item>
          <Form.Item name="valor" rules={[{ required: true, message: 'Informe o valor' }]}>
            <InputNumber placeholder="Valor" min={0} step={0.01} decimalSeparator="," style={{ width: 150 }} />
          </Form.Item>
          <Form.Item name="fonte">
            <Input placeholder="Fonte (ex.: Portaria nº)" style={{ width: 220 }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<PlusOutlined />} loading={cadastrar.isPending}>
              Cadastrar
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card>
        <Space direction="vertical" style={{ width: '100%' }}>
          {isError && !valores.length && (
            <Alert
              type="error"
              showIcon
              message="Não foi possível carregar os valores de referência. O cadastro fica indisponível até carregar."
              action={
                <Button size="small" onClick={() => refetch()}>
                  Tentar novamente
                </Button>
              }
            />
          )}
          <Input.Search placeholder="Filtrar parâmetros" allowClear onChange={(e) => setFiltro(e.target.value)} style={{ maxWidth: 360 }} />
          <Table
            size="small"
            rowKey="id"
            loading={isLoading}
            columns={colunas}
            dataSource={filtrados}
            pagination={false}
            scroll={{ x: 800 }}
          />
        </Space>
      </Card>
    </Space>
  );
};

export default ValoresReferencia;
