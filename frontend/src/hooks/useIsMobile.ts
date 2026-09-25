/**
 * Hook de responsividade baseado nos breakpoints do Ant Design.
 * Retorna true quando a largura está abaixo do breakpoint `md` (< 768px),
 * padronizando a detecção de mobile em toda a aplicação.
 */
import { Grid } from 'antd';

const { useBreakpoint } = Grid;

export function useIsMobile(): boolean {
  const screens = useBreakpoint();
  // screens.md é true a partir de 768px; ausência => mobile.
  return !screens.md;
}

export default useIsMobile;
