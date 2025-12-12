import { Row, Col, Typography, Empty } from 'antd';
import { useMunicipioStore } from '../../stores/municipioStore';
import { ProgramaCard } from './ProgramaCard';
import type { DetalhamentoPrograma } from '../../types';

const { Title, Text } = Typography;

export const ProgramasCards: React.FC = () => {
  const dadosProgramas = useMunicipioStore((state) => state.dadosProgramas);

  if (!dadosProgramas || dadosProgramas.length === 0) {
    return (
      <div style={{ padding: '40px 0', textAlign: 'center' }}>
        <Empty description="Nenhum programa disponível" />
      </div>
    );
  }

  // Agrupar programas por tema
  const saudeFamilia = dadosProgramas.filter((p) => ['esf-eap', 'acs'].includes(p.codigo));
  const saudeBucal = dadosProgramas.filter((p) => ['esb', 'ceo', 'sesb', 'lrpd'].includes(p.codigo));
  const emulti = dadosProgramas.filter((p) => p.codigo === 'emulti');
  const outros = dadosProgramas.filter((p) => ['demais', 'perdapita'].includes(p.codigo));

  const renderSecao = (titulo: string, icone: string, programas: DetalhamentoPrograma[], cor: string) => {
    if (programas.length === 0) return null;

    return (
      <div style={{ marginBottom: '32px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '16px',
            paddingBottom: '8px',
            borderBottom: `2px solid ${cor}`,
          }}
        >
          <span style={{ fontSize: '24px' }}>{icone}</span>
          <Title level={4} style={{ margin: 0, color: cor }}>
            {titulo}
          </Title>
          <Text type="secondary" style={{ marginLeft: 'auto' }}>
            {programas.length} {programas.length === 1 ? 'programa' : 'programas'}
          </Text>
        </div>
        <Row gutter={[16, 16]}>
          {programas.map((programa) => (
            <Col
              key={programa.codigo}
              xs={24} // Mobile: 1 coluna
              sm={24} // Tablet pequeno: 1 coluna
              md={12} // Tablet: 2 colunas
              lg={8} // Desktop: 3 colunas
              xl={8} // Desktop grande: 3 colunas
            >
              <ProgramaCard programa={programa} />
            </Col>
          ))}
        </Row>
      </div>
    );
  };

  return (
    <div style={{ marginBottom: '24px' }}>
      <Title level={4} style={{ marginBottom: '24px' }}>
        📊 Detalhamento por Programa
      </Title>

      {/* Saúde da Família e eAP */}
      {renderSecao('Saúde da Família e eAP', '👥', saudeFamilia, '#f59e0b')}

      {/* Saúde Bucal */}
      {renderSecao('Saúde Bucal', '🦷', saudeBucal, '#0ea5e9')}

      {/* Equipes Multiprofissionais */}
      {renderSecao('Equipes Multiprofissionais', '🏥', emulti, '#22c55e')}

      {/* Outros Programas */}
      {renderSecao('Outros Programas', '⚙️', outros, '#64748b')}
    </div>
  );
};
