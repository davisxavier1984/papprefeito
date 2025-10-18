import { Progress } from 'antd';

interface ProgressBarProps {
  atual: number;
  total: number;
  cor?: string;
  mostrarTexto?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  atual,
  total,
  cor = '#0ea5e9',
  mostrarTexto = true,
}) => {
  const percentual = total > 0 ? Math.round((atual / total) * 100) : 0;

  // Determinar cor baseada no percentual se não foi fornecida
  let corFinal = cor;
  if (cor === '#0ea5e9') { // Cor padrão
    if (percentual >= 100) {
      corFinal = '#22c55e'; // Verde
    } else if (percentual >= 75) {
      corFinal = '#0ea5e9'; // Azul
    } else if (percentual >= 50) {
      corFinal = '#f59e0b'; // Laranja
    } else {
      corFinal = '#ef4444'; // Vermelho
    }
  }

  return (
    <div style={{ width: '100%' }}>
      <Progress
        percent={Math.min(percentual, 100)}
        strokeColor={corFinal}
        trailColor="#e5e7eb"
        showInfo={false}
        size="small"
      />
      {mostrarTexto && (
        <div
          style={{
            fontSize: '12px',
            color: '#64748b',
            marginTop: '4px',
            textAlign: 'center',
          }}
        >
          {atual} / {total} ({percentual}%)
        </div>
      )}
    </div>
  );
};
