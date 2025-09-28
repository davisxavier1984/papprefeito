/**
 * Sidebar com seleções de parâmetros
 */

import React from 'react';
import { Layout, Typography, Divider, Space, Button, Alert } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import UFSelector from '../Selectors/UFSelector';
import MunicipioSelector from '../Selectors/MunicipioSelector';
import CompetenciaInput from '../Selectors/CompetenciaInput';
import { useCanConsult, useMunicipioStore } from '../../stores/municipioStore';

const { Sider } = Layout;
const { Title } = Typography;

const Sidebar: React.FC = () => {
  const canConsult = useCanConsult();
  const { isLoading, error, resetState } = useMunicipioStore();

  const handleConsultar = () => {
    // Esta função será implementada quando criarmos o hook de consulta
    console.log('Consultar dados...');
  };

  const handleReset = () => {
    resetState();
  };

  return (
    <Sider
      width={350}
      style={{
        background: '#f5f5f5',
        padding: '24px 16px',
        borderRight: '1px solid #d9d9d9'
      }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div>
          <Title level={4} style={{ marginBottom: 16 }}>
            📊 Seleção de Parâmetros
          </Title>

          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <UFSelector />
            <MunicipioSelector />
            <CompetenciaInput />
          </Space>
        </div>

        <Divider style={{ margin: '16px 0' }} />

        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleConsultar}
            disabled={!canConsult || isLoading}
            loading={isLoading}
            block
            size="large"
          >
            {isLoading ? 'Consultando...' : '🔍 Consultar'}
          </Button>

          <Button
            icon={<ReloadOutlined />}
            onClick={handleReset}
            disabled={isLoading}
            block
          >
            Limpar Seleções
          </Button>
        </Space>

        {error && (
          <Alert
            message="Erro na Consulta"
            description={error}
            type="error"
            showIcon
            closable
            onClose={() => useMunicipioStore.getState().setError(null)}
          />
        )}

        <Divider style={{ margin: '16px 0' }} />

        <div style={{ fontSize: '12px', color: '#666', lineHeight: 1.4 }}>
          <strong>Como usar:</strong><br />
          1. Selecione a UF<br />
          2. Selecione o município<br />
          3. Informe a competência (AAAAMM)<br />
          4. Clique em "Consultar"<br />
          5. Edite os valores na tabela
        </div>
      </Space>
    </Sider>
  );
};

export default Sidebar;